"""
SQLAlchemy models — mapped directly from the Police FIR ER Diagram
(Karnataka Police Department, DB schema doc). This covers the tables that
routes/search.py and routes/chatbot_rag.py actually query. The full ER
diagram has more tables (Court, Employee, Rank, Designation,
ArrestSurrender, ChargesheetDetails, Act/Section, etc.) — add those here
following the same pattern as your team fills out more features.

IMPORTANT: this file has not been run against a real database. Verify
column types/lengths against your actual DDL before running migrations.
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class District(Base):
    __tablename__ = "District"
    DistrictID = Column(Integer, primary_key=True)
    DistrictName = Column(String, nullable=False)
    StateID = Column(Integer)
    Active = Column(Integer, default=1)


class Unit(Base):
    __tablename__ = "Unit"
    UnitID = Column(Integer, primary_key=True)
    UnitName = Column(String, nullable=False)
    TypeID = Column(Integer)
    DistrictID = Column(Integer, ForeignKey("District.DistrictID"))
    StateID = Column(Integer)
    Active = Column(Integer, default=1)


class CrimeHead(Base):
    __tablename__ = "CrimeHead"
    CrimeHeadID = Column(Integer, primary_key=True)
    CrimeGroupName = Column(String, nullable=False)
    Active = Column(Integer, default=1)


class CrimeSubHead(Base):
    __tablename__ = "CrimeSubHead"
    CrimeSubHeadID = Column(Integer, primary_key=True)
    CrimeHeadID = Column(Integer, ForeignKey("CrimeHead.CrimeHeadID"))
    CrimeHeadName = Column(String, nullable=False)  # e.g. "Theft", "Murder" — the actual crime-type name
    SeqID = Column(Integer)


class CaseStatusMaster(Base):
    __tablename__ = "CaseStatusMaster"
    CaseStatusID = Column(Integer, primary_key=True)
    CaseStatusName = Column(String, nullable=False)  # "Under Investigation", "Charge Sheeted", "Closed", ...


class CaseMaster(Base):
    __tablename__ = "CaseMaster"
    CaseMasterID = Column(Integer, primary_key=True)
    CrimeNo = Column(String, nullable=False, unique=True)
    CaseNo = Column(String)
    CrimeRegisteredDate = Column(Date, nullable=False)
    PolicePersonID = Column(Integer)  # FK -> Employee.EmployeeID (Employee model not yet added here)
    PoliceStationID = Column(Integer, ForeignKey("Unit.UnitID"), nullable=False)
    CaseCategoryID = Column(Integer)
    GravityOffenceID = Column(Integer)
    CrimeMajorHeadID = Column(Integer, ForeignKey("CrimeHead.CrimeHeadID"))
    CrimeMinorHeadID = Column(Integer, ForeignKey("CrimeSubHead.CrimeSubHeadID"), nullable=False)
    CaseStatusID = Column(Integer, ForeignKey("CaseStatusMaster.CaseStatusID"), nullable=False)
    CourtID = Column(Integer)
    IncidentFromDate = Column(DateTime)
    IncidentToDate = Column(DateTime)
    InfoReceivedPSDate = Column(DateTime)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    BriefFacts = Column(Text)

    station = relationship("Unit")
    crime_sub_head = relationship("CrimeSubHead")
    status = relationship("CaseStatusMaster")


class Victim(Base):
    __tablename__ = "Victim"
    VictimMasterID = Column(Integer, primary_key=True)
    CaseMasterID = Column(Integer, ForeignKey("CaseMaster.CaseMasterID"), nullable=False)
    VictimName = Column(String, nullable=False)
    AgeYear = Column(Integer)
    GenderID = Column(String)  # M / F / T per the ER doc
    VictimPolice = Column(Integer, default=0)


class Accused(Base):
    __tablename__ = "Accused"
    AccusedMasterID = Column(Integer, primary_key=True)
    CaseMasterID = Column(Integer, ForeignKey("CaseMaster.CaseMasterID"), nullable=False)
    AccusedName = Column(String, nullable=False)
    AgeYear = Column(Integer)
    GenderID = Column(String)
    PersonID = Column(String)  # e.g. "A1", "A2"


# NOTE on the Weapon/Evidence gap flagged earlier: there is no
# Weapon/EvidenceType table anywhere in the ER diagram provided. If the
# team wants weapon-based search/analytics for real (not just the
# prototype's synthetic field), add a table here, e.g.:
#
# class WeaponEvidence(Base):
#     __tablename__ = "WeaponEvidence"
#     WeaponEvidenceID = Column(Integer, primary_key=True)
#     CaseMasterID = Column(Integer, ForeignKey("CaseMaster.CaseMasterID"))
#     WeaponType = Column(String)
