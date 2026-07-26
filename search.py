# app/routes/search.py
#
# Dynamic Criminal Search endpoint, built against the fields that actually
# exist in the Police FIR ER schema (CaseMaster, Victim, Accused, Unit,
# District, CrimeSubHead, CaseStatusMaster). Drop into app/routes/ once the
# real database and SQLAlchemy models exist, and wire the two "REPLACE ME"
# marked sections to the team's actual models/session.
#
# Design notes (why it's built this way):
# - Every filter is OPTIONAL. None are required, so the frontend can send
#   only the fields the user actually filled in.
# - Filters combine with AND logic (requirement: multiple filters at once).
# - Dropdown "vocabulary" endpoints return DISTINCT values that exist in the
#   data right now, instead of a hardcoded list going stale.
# - No filter references a column that isn't in the ER diagram. Age and
#   gender come from Victim/Accused, not CaseMaster, since CaseMaster has
#   no person-level fields of its own.

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/search", tags=["Criminal Search"])

# ---- REPLACE ME: import your real models and session dependency ----
# from app.database import get_db
# from app.models import CaseMaster, Victim, Accused, Unit, District, CrimeSubHead, CaseStatusMaster
# ----------------------------------------------------------------------


class CaseSearchResult(BaseModel):
    crime_no: str
    case_no: str
    crime_type: str
    district: str
    police_station: str
    date_registered: date
    status: str
    victim_name: Optional[str] = None
    victim_age: Optional[int] = None
    victim_gender: Optional[str] = None
    accused_name: Optional[str] = None
    weapon: Optional[str] = None

    class Config:
        from_attributes = True


class PaginatedSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[CaseSearchResult]


@router.get("/cases", response_model=PaginatedSearchResponse)
def search_cases(
    crime_no: Optional[str] = Query(None, description="Partial match on CrimeNo / FIR number"),
    crime_type: Optional[str] = Query(None, description="Exact match on CrimeSubHead.CrimeHeadName"),
    status: Optional[str] = Query(None, description="Exact match on CaseStatusMaster.CaseStatusName"),
    district: Optional[str] = Query(None, description="Exact match on District.DistrictName"),
    police_station: Optional[str] = Query(None, description="Exact match on Unit.UnitName"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    victim_name: Optional[str] = Query(None, description="Partial match on Victim.VictimName"),
    offender_name: Optional[str] = Query(None, description="Partial match on Accused.AccusedName"),
    weapon: Optional[str] = Query(None, description="If a Weapon/EvidenceType table is added — not yet in the ER schema"),
    gender: Optional[str] = Query(None, description="Exact match on Victim.GenderID (M/F/T)"),
    age_min: Optional[int] = Query(None, ge=0, le=120),
    age_max: Optional[int] = Query(None, ge=0, le=120),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    sort_by: str = Query("date_registered", pattern="^(date_registered|crime_no|status)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    # db: Session = Depends(get_db),   # REPLACE ME: uncomment once get_db exists
):
    """
    Builds one dynamic, AND-combined SQL query from whichever filters were
    actually supplied. Any filter left as None is simply omitted from the
    WHERE clause instead of matching everything or raising an error.

    NOTE: 'weapon' is included per the requirements list, but the ER schema
    you shared has no Weapon/EvidenceType column anywhere in CaseMaster,
    Victim, or Accused. Either:
      (a) add a WeaponUsed column/table to the schema, or
      (b) drop this filter from both the UI and this endpoint.
    Leaving it wired but non-functional would violate "don't reference
    fields that don't exist in the dataset" — so right now it's a no-op
    filter (ignored) until the schema decision is made. Flag this to your
    team lead before shipping.
    """

    # ---- REPLACE ME: real SQLAlchemy query against your actual models ----
    # conditions = []
    # if crime_no:
    #     conditions.append(CaseMaster.CrimeNo.ilike(f"%{crime_no}%"))
    # if crime_type:
    #     conditions.append(CrimeSubHead.CrimeHeadName == crime_type)
    # if status:
    #     conditions.append(CaseStatusMaster.CaseStatusName == status)
    # if district:
    #     conditions.append(District.DistrictName == district)
    # if police_station:
    #     conditions.append(Unit.UnitName == police_station)
    # if date_from:
    #     conditions.append(CaseMaster.CrimeRegisteredDate >= date_from)
    # if date_to:
    #     conditions.append(CaseMaster.CrimeRegisteredDate <= date_to)
    # if victim_name:
    #     conditions.append(Victim.VictimName.ilike(f"%{victim_name}%"))
    # if offender_name:
    #     conditions.append(Accused.AccusedName.ilike(f"%{offender_name}%"))
    # if gender:
    #     conditions.append(Victim.GenderID == gender)
    # if age_min is not None:
    #     conditions.append(Victim.AgeYear >= age_min)
    # if age_max is not None:
    #     conditions.append(Victim.AgeYear <= age_max)
    #
    # query = (
    #     select(CaseMaster, Victim, Accused, Unit, District, CrimeSubHead, CaseStatusMaster)
    #     .join(Victim, Victim.CaseMasterID == CaseMaster.CaseMasterID, isouter=True)
    #     .join(Accused, Accused.CaseMasterID == CaseMaster.CaseMasterID, isouter=True)
    #     .join(Unit, Unit.UnitID == CaseMaster.PoliceStationID)
    #     .join(District, District.DistrictID == Unit.DistrictID)
    #     .join(CrimeSubHead, CrimeSubHead.CrimeSubHeadID == CaseMaster.CrimeMinorHeadID)
    #     .join(CaseStatusMaster, CaseStatusMaster.CaseStatusID == CaseMaster.CaseStatusID)
    #     .where(and_(*conditions))
    # )
    # sort_col = {"date_registered": CaseMaster.CrimeRegisteredDate,
    #             "crime_no": CaseMaster.CrimeNo,
    #             "status": CaseStatusMaster.CaseStatusName}[sort_by]
    # query = query.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
    #
    # total = db.scalar(select(func.count()).select_from(query.subquery()))
    # rows = db.execute(query.offset((page-1)*page_size).limit(page_size)).all()
    # results = [ ... map rows to CaseSearchResult ... ]
    # ------------------------------------------------------------------------

    raise NotImplementedError(
        "Wire this to your real database session and models — "
        "see the commented block above for the exact query shape."
    )


@router.get("/vocabulary")
def search_vocabulary(
    # db: Session = Depends(get_db),
):
    """
    Returns the DISTINCT values currently in the data for every dropdown —
    crime types, statuses, districts, stations, genders — so the frontend
    never hardcodes a list that can drift out of sync with the database.
    Populate each list with a `SELECT DISTINCT ... FROM ...` against the
    real tables, e.g.:
        SELECT DISTINCT CrimeHeadName FROM CrimeSubHead
        SELECT DISTINCT CaseStatusName FROM CaseStatusMaster
        SELECT DISTINCT DistrictName FROM District
        SELECT DISTINCT UnitName FROM Unit
        SELECT DISTINCT GenderID FROM Victim
    """
    raise NotImplementedError("Wire each list to a DISTINCT query against the real tables.")
