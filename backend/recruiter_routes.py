from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.db import SessionLocal
from backend.models import JobRole, JobRoleRequirementText, Recruiter, Interview, InterviewNote


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


class InterviewCreateIn(BaseModel):
    candidate_id: int
    role_id: int
    scheduled_time: Optional[str] = None


class NoteIn(BaseModel):
    notes: Optional[str] = None
    fit_score: Optional[int] = None
    decision: Optional[str] = None


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


@router.post("/{recruiter_id}/interviews")
def create_interview(recruiter_id: int, payload: InterviewCreateIn, db: Session = Depends(get_db)):
    recruiter = db.query(Recruiter).filter(Recruiter.recruiter_id == recruiter_id).first()
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")

    # Make sure role exists and belongs to recruiter's company
    role = db.query(JobRole).filter(JobRole.role_id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.company_id != recruiter.company_id:
        raise HTTPException(status_code=403, detail="Role does not belong to your company")

    # create interview
    interview = Interview(candidate_id=payload.candidate_id, recruiter_id=recruiter_id, role_id=payload.role_id,
                          scheduled_time=payload.scheduled_time, status=("scheduled" if payload.scheduled_time else "requested"))
    db.add(interview)
    db.commit()
    db.refresh(interview)

    return {"interview_id": interview.interview_id}


@router.post("/{recruiter_id}/interviews/{interview_id}/notes")
def create_or_update_note(recruiter_id: int, interview_id: int, payload: NoteIn, db: Session = Depends(get_db)):
    recruiter = db.query(Recruiter).filter(Recruiter.recruiter_id == recruiter_id).first()
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")

    interview = db.query(Interview).filter(Interview.interview_id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview.recruiter_id != recruiter_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this interview")

    existing = db.query(InterviewNote).filter(InterviewNote.interview_id == interview_id).first()
    if existing:
        if payload.notes is not None:
            existing.notes = payload.notes
        if payload.fit_score is not None:
            existing.fit_score = payload.fit_score
        if payload.decision is not None:
            existing.decision = payload.decision
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return {"ok": True, "note_id": existing.id}
    else:
        note = InterviewNote(interview_id=interview_id, recruiter_id=recruiter_id, notes=payload.notes, fit_score=payload.fit_score, decision=payload.decision)
        db.add(note)
        db.commit()
        db.refresh(note)
        return {"ok": True, "note_id": note.id}
