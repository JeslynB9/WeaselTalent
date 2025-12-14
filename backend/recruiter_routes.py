from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.db import SessionLocal
from backend.models import JobRole, JobRoleRequirementText, Recruiter


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
