# app/routes/chatbot_rag.py
#
# Crime & Safety Assistant — RAG pattern for the REAL backend (FastAPI + PostgreSQL
# + LangChain/Ollama or any LLM). This is the architecture to wire in once the actual
# database and LLM client exist — the prototype's JS engine (answerQuery() in the demo
# HTML) simulates this exact flow client-side for testing without a live model.
#
# Why it's structured this way:
# - The topic gate runs BEFORE any LLM call. Relying on the LLM's own judgment to
#   refuse off-topic questions is unreliable and costs a call either way — a cheap
#   deterministic gate is both cheaper and more reliable at enforcing "crime domain only."
# - Retrieval always runs SQL aggregates first; the LLM only narrates numbers that were
#   actually returned by the database. It is never given free rein to answer from its
#   own training data — that's what "must not hallucinate" requires structurally, not
#   just as a prompt instruction.
# - Every intent maps to ONE parameterized SQL template. No f-string SQL, no string
#   concatenation of user input into a query.
# - A simple in-memory TTL cache avoids re-running identical aggregate queries back to
#   back (requirement: performance/caching). Swap for Redis in production.

import re, time, hashlib
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/chatbot", tags=["Crime & Safety Assistant"])

# ---- REPLACE ME: real DB session + LLM client ----
# from app.database import get_db
# from app.llm_client import call_llm   # e.g. wraps langchain_ollama.ChatOllama
# ---------------------------------------------------

REFUSAL_MESSAGE = ("I am a Crime Intelligence Assistant and can only answer questions "
                    "related to crime data, public safety, and crime analytics.")

# ---- 1. Topic gate (runs before touching the DB or the LLM) ----
DOMAIN_TERMS = [
    "crime", "case", "fir", "safety", "safe", "danger", "risk", "police", "station",
    "district", "hotspot", "victim", "offender", "accused", "arrest", "chargesheet",
    "weapon", "statistic", "trend", "patrol", "curfew", "theft", "robbery", "murder",
    "assault", "burglary", "cyber", "narcotic", "rioting", "missing", "night", "morning",
    "evening", "hour", "peak", "weekday", "month", "location", "hotspot", "investigation",
    "solved", "pending", "closed", "latest", "recent",
]
def is_on_topic(question: str, db: "Session" = None) -> bool:
    q = question.lower()
    if any(term in q for term in DOMAIN_TERMS):
        return True
    # REPLACE ME: also check against DISTINCT district/station/crime-type names from the DB,
    # the same way the prototype builds its vocabulary from CASES, e.g.:
    # known_entities = db.execute(text("SELECT DistrictName FROM District UNION SELECT UnitName FROM Unit UNION SELECT CrimeHeadName FROM CrimeSubHead")).scalars().all()
    # return any(e.lower() in q for e in known_entities)
    return False


# ---- 2. Tiny TTL cache for repeated aggregate queries ----
_cache: dict[str, tuple[float, dict]] = {}
CACHE_TTL_SECONDS = 60

def cached(key: str, compute_fn):
    now = time.time()
    if key in _cache and now - _cache[key][0] < CACHE_TTL_SECONDS:
        return _cache[key][1]
    result = compute_fn()
    _cache[key] = (now, result)
    return result


# ---- 3. Intent detection -> parameterized SQL retrieval ----
# Each function returns the RAW retrieved rows/aggregates — nothing narrated yet.
# This is the "R" in RAG: retrieval happens in SQL, not in the LLM's head.

def retrieve_most_common_crime(db: Session) -> dict:
    def compute():
        row = db.execute(text("""
            SELECT csh.CrimeHeadName AS crime_type, COUNT(*) AS cnt
            FROM CaseMaster cm
            JOIN CrimeSubHead csh ON csh.CrimeSubHeadID = cm.CrimeMinorHeadID
            GROUP BY csh.CrimeHeadName
            ORDER BY cnt DESC LIMIT 1
        """)).mappings().first()
        total = db.execute(text("SELECT COUNT(*) FROM CaseMaster")).scalar()
        return {"top_type": dict(row) if row else None, "total_cases": total}
    return cached("most_common_crime", compute)

def retrieve_district_ranking(db: Session, order: str = "DESC") -> dict:
    def compute():
        rows = db.execute(text(f"""
            SELECT d.DistrictName AS district, COUNT(*) AS cnt
            FROM CaseMaster cm
            JOIN Unit u ON u.UnitID = cm.PoliceStationID
            JOIN District d ON d.DistrictID = u.DistrictID
            GROUP BY d.DistrictName
            ORDER BY cnt {order}
        """)).mappings().all()
        return {"ranking": [dict(r) for r in rows]}
    return cached(f"district_ranking_{order}", compute)

def retrieve_peak_hour(db: Session, hour: Optional[int] = None) -> dict:
    def compute():
        # EXTRACT(HOUR FROM ...) requires a real timestamp column — IncidentFromDate per the ER schema
        rows = db.execute(text("""
            SELECT EXTRACT(HOUR FROM IncidentFromDate)::int AS hr, COUNT(*) AS cnt
            FROM CaseMaster
            GROUP BY hr ORDER BY cnt DESC
        """)).mappings().all()
        return {"hourly": [dict(r) for r in rows]}
    key = f"peak_hour_{hour}"
    data = cached(key, compute)
    if hour is not None:
        data["requested_hour_count"] = next((r["cnt"] for r in data["hourly"] if r["hr"] == hour), 0)
    return data

def retrieve_latest_crime(db: Session) -> dict:
    def compute():
        row = db.execute(text("""
            SELECT cm.CrimeNo, csh.CrimeHeadName AS crime_type, cm.CrimeRegisteredDate,
                   cm.latitude, cm.longitude, csm.CaseStatusName AS status,
                   d.DistrictName AS district, u.UnitName AS station
            FROM CaseMaster cm
            JOIN CrimeSubHead csh ON csh.CrimeSubHeadID = cm.CrimeMinorHeadID
            JOIN CaseStatusMaster csm ON csm.CaseStatusID = cm.CaseStatusID
            JOIN Unit u ON u.UnitID = cm.PoliceStationID
            JOIN District d ON d.DistrictID = u.DistrictID
            ORDER BY cm.CrimeRegisteredDate DESC, cm.IncidentFromDate DESC
            LIMIT 1
        """)).mappings().first()
        return dict(row) if row else None
    return cached("latest_crime", compute)  # short TTL matters most here — this one should barely cache


# ---- 4. Grounded LLM narration ----
SYSTEM_PROMPT = """You are a Crime & Safety Assistant for the Karnataka State Police.
Rules you must follow exactly:
1. Use ONLY the data provided to you in the "RETRIEVED DATA" section below. Never use
   outside knowledge, training data, or assumptions about crime statistics.
2. If the retrieved data is empty or does not answer the question, say exactly:
   "The dataset does not contain sufficient information to answer that."
3. Structure every response with these exact section headers: Analysis, Supporting
   Statistics, Conclusion, Safety Recommendation.
4. Never answer questions unrelated to crime, public safety, or this dataset.
5. Do not invent case numbers, names, coordinates, or statistics not present in the
   retrieved data.
"""

def build_prompt(question: str, retrieved: dict) -> str:
    return f"{SYSTEM_PROMPT}\n\nUSER QUESTION: {question}\n\nRETRIEVED DATA:\n{retrieved}\n\nRespond now, following the required structure."


class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    on_topic: bool
    retrieved_data: Optional[dict] = None  # returned for explainability/auditing


@router.post("/ask", response_model=ChatResponse)
def ask_chatbot(req: ChatRequest):  # , db: Session = Depends(get_db)
    if not is_on_topic(req.question):
        return ChatResponse(answer=REFUSAL_MESSAGE, on_topic=False, retrieved_data=None)

    q = req.question.lower()

    # ---- REPLACE ME: this if/elif intent router is illustrative for 3 intents;
    # extend with one retrieve_* function per intent listed in the requirements
    # (station ranking, weekday ranking, hotspot ranking, monthly trend, type+status
    # counts, etc.) following the exact same retrieve -> narrate pattern. ----
    # if "most common crime" in q:
    #     retrieved = retrieve_most_common_crime(db)
    # elif "latest crime" in q or "recent crime" in q:
    #     retrieved = retrieve_latest_crime(db)
    # elif re.search(r"\d{1,2}\s?(am|pm)", q) or "peak hour" in q:
    #     retrieved = retrieve_peak_hour(db)
    # elif "highest crime" in q and "district" in q:
    #     retrieved = retrieve_district_ranking(db, order="DESC")
    # elif "safest district" in q:
    #     retrieved = retrieve_district_ranking(db, order="ASC")
    # else:
    #     retrieved = None
    #
    # if retrieved is None:
    #     return ChatResponse(answer="The dataset does not contain sufficient information to answer that.",
    #                          on_topic=True, retrieved_data=None)
    #
    # prompt = build_prompt(req.question, retrieved)
    # llm_answer = call_llm(prompt)   # your LangChain/Ollama call
    # return ChatResponse(answer=llm_answer, on_topic=True, retrieved_data=retrieved)

    raise NotImplementedError("Wire the intent router above to your real DB session and LLM client.")
