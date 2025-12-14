from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.db import SessionLocal
from backend.models import JobRole, JobRoleRequirementText, Recruiter
from datetime import datetime
from db import get_db
from models import (
    RecruiterAvailability,
    Interview,
    InterviewStatus,
)

class AvailabilityIn(BaseModel):
    start_time: datetime
    end_time: datetime

class InterviewScheduleIn(BaseModel):
    candidate_id: int
    role_id: int
    scheduled_time: datetime

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RequirementIn(BaseModel):
    requirement_text: str
    level: Optional[int] = None


class RoleCreate(BaseModel):
    company_id: int
    title: str
    description: Optional[str] = None
    requirements: Optional[List[RequirementIn]] = None
    role_id: Optional[int] = None


router = APIRouter(prefix="/recruiters", tags=["recruiters"])


@router.post("/{recruiter_id}/roles")
def create_role(recruiter_id: int, payload: RoleCreate, db: Session = Depends(get_db)):
    # verify recruiter exists and belongs to company
    recruiter = db.query(Recruiter).filter(Recruiter.recruiter_id == recruiter_id).first()
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")

    if recruiter.company_id != payload.company_id:
        raise HTTPException(status_code=403, detail="Recruiter does not belong to this company")

    # create the job role
    role = JobRole(company_id=payload.company_id, title=payload.title, description=payload.description)
    db.add(role)
    db.commit()
    db.refresh(role)

    # store free-text requirements if provided
    if payload.requirements:
        for r in payload.requirements:
            req = JobRoleRequirementText(role_id=role.role_id, requirement_text=r.requirement_text, level=r.level)
            db.add(req)
        db.commit()

    return {"role_id": role.role_id}

@router.post("/{recruiter_id}/availability")
def add_availability(
    recruiter_id: int,
    payload: AvailabilityIn,
    db: Session = Depends(get_db),
):
    if payload.end_time <= payload.start_time:
        raise HTTPException(400, "End time must be after start time")

    slot = RecruiterAvailability(
        recruiter_id=recruiter_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        is_booked=False,
    )

    db.add(slot)
    db.commit()
    db.refresh(slot)

    return {
        "availability_id": slot.availability_id,
        "start_time": slot.start_time,
        "end_time": slot.end_time,
    }

@router.get("/{recruiter_id}/availability")
def list_availability(
    recruiter_id: int,
    db: Session = Depends(get_db),
):
    slots = (
        db.query(RecruiterAvailability)
        .filter(
            RecruiterAvailability.recruiter_id == recruiter_id,
            RecruiterAvailability.is_booked == False,
        )
        .order_by(RecruiterAvailability.start_time)
        .all()
    )

    return slots

@router.get("/{recruiter_id}/roles")
def list_roles(recruiter_id: int, db: Session = Depends(get_db)):
    """
    List job roles that belong to the recruiter's company.
    """
    recruiter = db.query(Recruiter).filter(Recruiter.recruiter_id == recruiter_id).first()
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")

    roles = db.query(JobRole).filter(JobRole.company_id == recruiter.company_id).all()

    out = []
    for r in roles:
        reqs = db.query(JobRoleRequirementText).filter(JobRoleRequirementText.role_id == r.role_id).all()
        out.append({
            "role_id": r.role_id,
            "company_id": r.company_id,
            "title": r.title,
            "description": r.description,
            "requirements": [{"id": q.id, "text": q.requirement_text, "level": q.level} for q in reqs]
        })

    return out

