"""
Crime Analysis — pandas mirror of the analytics logic used throughout the
frontend prototype (dashboard KPIs, chatbot answers, hotspot ranking,
predictions). Run this directly to print a full analytics report, or
import the functions into a notebook / real backend service.

Run:  python crime_analysis.py
Requires: pandas (pip install pandas)
"""

import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "dataset" / "crime_cases.csv"
REFERENCE_DATE = pd.Timestamp("2026-07-24")  # "today" for all recency-based analysis


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["date_registered"])
    df["weekday"] = df["date_registered"].dt.day_name()
    df["month"] = df["date_registered"].dt.month
    df["is_weekend"] = df["weekday"].isin(["Saturday", "Sunday"])
    return df


def most_common_crime(df: pd.DataFrame) -> pd.Series:
    return df["crime_type"].value_counts()


def district_ranking(df: pd.DataFrame) -> pd.Series:
    return df["district"].value_counts().sort_values(ascending=False)


def station_ranking(df: pd.DataFrame) -> pd.Series:
    return df["police_station"].value_counts().sort_values(ascending=False)


def hourly_distribution(df: pd.DataFrame) -> pd.Series:
    return df["hour"].value_counts().sort_index()


def peak_and_safe_hours(df: pd.DataFrame) -> tuple[int, int]:
    hourly = hourly_distribution(df)
    return int(hourly.idxmax()), int(hourly.idxmin())


def weekday_ranking(df: pd.DataFrame) -> pd.Series:
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return df["weekday"].value_counts().reindex(order)


def monthly_trend(df: pd.DataFrame) -> pd.Series:
    return df["month"].value_counts().sort_index()


def weekend_vs_weekday(df: pd.DataFrame) -> pd.Series:
    return df["is_weekend"].value_counts()


def status_breakdown(df: pd.DataFrame) -> pd.Series:
    return df["status"].value_counts()


def hotspot_ranking(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    grouped = (
        df.groupby("police_station")
        .agg(total_crimes=("case_id", "count"),
             district=("district", "first"),
             latitude=("latitude", "mean"),
             longitude=("longitude", "mean"))
        .sort_values("total_crimes", ascending=False)
    )
    return grouped.head(top_n)


def safety_score(df: pd.DataFrame, place_col: str, place_value: str) -> dict:
    """
    Mirrors the frontend's safety-score heuristic:
      score = max(5, 100 - round(total / max_peer_total * 90))
    where "peer group" is all districts if place_col == 'district',
    or all stations if place_col == 'police_station'.
    This is an illustrative demo heuristic, NOT a validated risk model.
    """
    peer_totals = df[place_col].value_counts()
    total = int(peer_totals.get(place_value, 0))
    max_peer = int(peer_totals.max()) if len(peer_totals) else 1
    score = max(5, 100 - round(total / max_peer * 90))
    risk = "Low" if score >= 70 else "Medium" if score >= 40 else "High"
    return {"place": place_value, "total_cases": total, "safety_score": score, "risk_level": risk}


def repeat_offenders(df: pd.DataFrame, min_cases: int = 2) -> pd.DataFrame:
    counts = df.groupby(["accused_id", "accused_name"]).size().reset_index(name="case_count")
    return counts[counts["case_count"] >= min_cases].sort_values("case_count", ascending=False)


def chargesheet_sla_overdue(df: pd.DataFrame, threshold_days: int = 45) -> pd.DataFrame:
    open_cases = df[df["status"] == "Under Investigation"].copy()
    open_cases["days_open"] = (REFERENCE_DATE - open_cases["date_registered"]).dt.days
    return open_cases[open_cases["days_open"] > threshold_days].sort_values("days_open", ascending=False)


def weekly_change(df: pd.DataFrame) -> dict:
    last7 = df[(REFERENCE_DATE - df["date_registered"]).dt.days.between(0, 6)]
    prev7 = df[(REFERENCE_DATE - df["date_registered"]).dt.days.between(7, 13)]
    last7_n, prev7_n = len(last7), len(prev7)
    pct = round((last7_n - prev7_n) / prev7_n * 100) if prev7_n else (100 if last7_n else 0)
    return {"last_7_days": last7_n, "previous_7_days": prev7_n, "pct_change": pct}


if __name__ == "__main__":
    df = load_data()
    print(f"Loaded {len(df)} cases\n")

    print("=== Most Common Crime Types ===")
    print(most_common_crime(df), "\n")

    print("=== District Ranking (highest to lowest) ===")
    print(district_ranking(df), "\n")

    print("=== Top 5 Hotspot Stations ===")
    print(hotspot_ranking(df), "\n")

    peak_h, safe_h = peak_and_safe_hours(df)
    print(f"Peak crime hour: {peak_h}:00  |  Safest hour: {safe_h}:00\n")

    print("=== Weekday Ranking ===")
    print(weekday_ranking(df), "\n")

    print("=== Monthly Trend ===")
    print(monthly_trend(df), "\n")

    print("=== Status Breakdown ===")
    print(status_breakdown(df), "\n")

    print("=== Weekly Change ===")
    print(weekly_change(df), "\n")

    print("=== Repeat Offenders (2+ cases) ===")
    print(repeat_offenders(df), "\n")

    print("=== Chargesheet SLA Overdue (>45 days, Under Investigation) ===")
    print(chargesheet_sla_overdue(df)[["crime_no", "district", "crime_type", "days_open"]], "\n")

    top_district = district_ranking(df).idxmax()
    print(f"=== Safety Score example: {top_district} ===")
    print(safety_score(df, "district", top_district))
