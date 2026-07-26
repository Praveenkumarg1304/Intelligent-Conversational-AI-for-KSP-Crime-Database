# Data Dictionary — `crime_cases.csv` / `crime_cases.json`

90 records, synthetically generated to match the real Police FIR ER schema
(Karnataka Police Department), mapped onto real Karnataka district and
police station coordinates. **No real case data** — every name, phone
number, and coordinate jitter is fabricated for this prototype.

| Column | Type | Description |
|---|---|---|
| `case_id` | string | Internal row identifier (not a real FIR field) |
| `crime_no` | string | FIR number, format: 1-digit category + 4-digit district ID + 4-digit station ID + 4-digit year + 5-digit serial (per `CaseMaster.CrimeNo` in the ER diagram) |
| `case_no` | string | Last 9 digits of `crime_no` (per `CaseMaster.CaseNo`) |
| `district` | string | One of 10 real Karnataka districts |
| `police_station` | string | Police station name within the district |
| `latitude` / `longitude` | float | Real district/station coordinates with small random jitter |
| `crime_type` | string | e.g. Theft, Robbery, Murder, Cyber Fraud, NDPS Offence, etc. (maps to `CrimeSubHead.CrimeHeadName`) |
| `crime_head` | string | Major crime group (maps to `CrimeHead.CrimeGroupName`), e.g. "Crimes Against Property" |
| `act_section` | string | Illustrative BNS/IT Act/NDPS Act section — **not legally verified**, for demo only |
| `is_heinous` | bool | Gravity flag (maps to `GravityOffence`) |
| `date_registered` | date (YYYY-MM-DD) | Jan 1 – Jul 24, 2026 |
| `hour` | int (0–23) | Hour of incident |
| `time_of_day` | string | Morning / Afternoon / Evening / Night bucket derived from `hour` |
| `status` | string | Under Investigation / Charge Sheeted / Closed / Undetected (maps to `CaseStatusMaster`) |
| `weapon` | string | **Not in the real ER schema** — see note below |
| `victim_name`, `victim_age`, `victim_gender` | — | Maps to `Victim` table |
| `accused_name`, `accused_age`, `accused_gender`, `accused_id` | — | Maps to `Accused` table (`accused_id` mirrors `PersonID`, e.g. "A/1042") |
| `investigating_officer` | string | Fictional officer name (maps to `Employee` via `CaseMaster.PolicePersonID`) |
| `court` | string | Fictional court name (maps to `Court`) |
| `brief_facts` | string | Short synthetic case summary (maps to `CaseMaster.BriefFacts`) |

## Known schema gap
`weapon` has no backing table in the real ER diagram provided by the team.
It's included here for the prototype's search/analytics features, but the
real database needs a `WeaponEvidence` table (or similar) added before this
field means anything against real data — see `backend/app/models.py` for
a suggested addition.

## Reference date
All "recent"/"this month"/"last 30 days" style analytics in the app use
**July 24, 2026** as the reference "today".
