from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from db import SessionLocal
from models import CandidateSkillLevel, TechnicalDomain

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter (
    prefix="/candidate",
    tags=["candidate"]
)

class CandidateDomainsIn(BaseModel):
    user_id: int
    domains: List[str]

@router.post("/domains")
def save_candidate_domains (
    payload: CandidateDomainsIn,
    db: Session = Depends(get_db)
):
    user_id = payload.user_id
    domain_names = payload.domains
    # remove existing domain selection for this user
    db.query(CandidateSkillLevel).filter (
        CandidateSkillLevel.candidate_id == user_id
    ).delete()

    # fetch domain records by name
    domains = db.query(TechnicalDomain).filter (
        TechnicalDomain.name.in_(domain_names)
    ).all()

    if len(domains) != len(domain_names):
        raise HTTPException (
            status_code = 400,
            detail = "One or more domains are invalid"
        )
    
    # insert new domain selections
    for domain in domains:
        db.add (
            CandidateSkillLevel (
                candidate_id = user_id,
                domain_id = domain.domain_id,
                level = 0
            )
        )
    db.commit()
    return {"status": "ok"}

# load selected domains
@router.get("/domains/{user_id}", response_model=List[str])
def get_candidate_domains (
    user_id: int,
    db: Session = Depends(get_db)
):
    rows = (
        db.query(TechnicalDomain.name).join (
            CandidateSkillLevel,
            CandidateSkillLevel.domain_id == TechnicalDomain.domain_id
        )
        .filter(CandidateSkillLevel.candidate_id == user_id)
        .all()
    )

    return [row[0] for row in rows]