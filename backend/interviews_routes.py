from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import SessionLocal
from backend.models import Interview, InterviewNote, JobRole


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.get("/{interview_id}/notes")
def get_interview_notes(interview_id: int, candidate_id: int = None, db: Session = Depends(get_db)):
    # Optionally validate candidate owns the interview
    interview = db.query(Interview).filter(Interview.interview_id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    if candidate_id is not None and interview.candidate_id != candidate_id:
        raise HTTPException(status_code=403, detail="Not authorized to view notes for this interview")

    note = db.query(InterviewNote).filter(InterviewNote.interview_id == interview_id).first()
    if not note:
        return {"notes": None}

    return {
        "notes": note.notes,
        "fit_score": note.fit_score,
        "decision": note.decision,
        "recruiter_id": note.recruiter_id,
    }



@router.get("/candidates/{candidate_id}/interviews")
def list_candidate_interviews(candidate_id: int, db: Session = Depends(get_db)):
    """Return interviews for a candidate including basic role info and whether notes exist."""
    rows = db.query(Interview).filter(Interview.candidate_id == candidate_id).all()
    out = []
    for r in rows:
        role = db.query(JobRole).filter(JobRole.role_id == r.role_id).first()
        note = db.query(InterviewNote).filter(InterviewNote.interview_id == r.interview_id).first()
        out.append({
            "interview_id": r.interview_id,
            "role_id": r.role_id,
            "role_title": role.title if role else None,
            "status": r.status,
            "has_notes": bool(note),
            "notes_preview": (note.notes[:200] + '...') if note and len(note.notes) > 200 else (note.notes if note else None),
            "fit_score": note.fit_score if note else None,
        })
    return out
