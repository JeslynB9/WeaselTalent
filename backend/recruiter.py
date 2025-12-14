# recruiter functions
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from backend.cors_config import add_cors_middleware

DB_PATH = "lyrathon_recruiter.db"
app = FastAPI(title="Recruiter Backend (Lyrathon)", version="1.0")

add_cors_middleware(app)


# -----------------------------
# DB helpers
# -----------------------------
def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# -----------------------------
# Schema (subset of your ERD)
# -----------------------------
def init_db() -> None:
    conn = db()
    cur = conn.cursor()

    # User (login identity)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS User (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT,
        role TEXT NOT NULL CHECK(role IN ('candidate','recruiter','admin')),
        created_at TEXT NOT NULL,
        last_login TEXT,
        is_active INTEGER NOT NULL DEFAULT 1
    )
    """)

    # UserProfile (candidate personal info + anonymity)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS UserProfile (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        dob TEXT,
        photo TEXT,
        is_anonymous INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES User(user_id)
    )
    """)

    # Companies
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Companies (
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # Recruiters (belongs to company + maps to a user)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Recruiters (
        recruiter_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        company_id INTEGER NOT NULL,
        job_title TEXT,
        FOREIGN KEY(user_id) REFERENCES User(user_id),
        FOREIGN KEY(company_id) REFERENCES Companies(company_id)
    )
    """)

    # JobRoles (roles posted by company)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS JobRoles (
        role_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY(company_id) REFERENCES Companies(company_id)
    )
    """)

    # CandidateJobMatches (precomputed match scores)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS CandidateJobMatches (
        candidate_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        match_score REAL NOT NULL,
        last_updated TEXT NOT NULL,
        PRIMARY KEY(candidate_id, role_id),
        FOREIGN KEY(candidate_id) REFERENCES User(user_id),
        FOREIGN KEY(role_id) REFERENCES JobRoles(role_id)
    )
    """)

    # RecruiterAvailability (time slots)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS RecruiterAvailability (
        availability_id INTEGER PRIMARY KEY AUTOINCREMENT,
        recruiter_id INTEGER NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        is_booked INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(recruiter_id) REFERENCES Recruiters(recruiter_id)
    )
    """)

    # Interviews (links candidate + recruiter + role)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Interviews (
        interview_id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL,
        recruiter_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        scheduled_time TEXT,
        status TEXT NOT NULL CHECK(status IN ('requested','scheduled','completed','cancelled')) DEFAULT 'requested',
        FOREIGN KEY(candidate_id) REFERENCES User(user_id),
        FOREIGN KEY(recruiter_id) REFERENCES Recruiters(recruiter_id),
        FOREIGN KEY(role_id) REFERENCES JobRoles(role_id)
    )
    """)

    # InterviewNotes (recruiter notes + decision)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS InterviewNotes (
        interview_id INTEGER PRIMARY KEY,
        recruiter_id INTEGER NOT NULL,
        notes TEXT,
        fit_score INTEGER CHECK(fit_score BETWEEN 1 AND 10),
        decision TEXT CHECK(decision IN ('advance','reject','pending')) DEFAULT 'pending',
        FOREIGN KEY(interview_id) REFERENCES Interviews(interview_id),
        FOREIGN KEY(recruiter_id) REFERENCES Recruiters(recruiter_id)
    )
    """)

    # Notifications
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Notifications (
        notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES User(user_id)
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# Seed demo data (so UI works immediately)
# -----------------------------
def seed_demo() -> None:
    conn = db()
    cur = conn.cursor()

    # Create a company
    cur.execute("INSERT OR IGNORE INTO Companies(company_id, name, description, created_at) VALUES (1,?,?,?)",
                ("Talent Co", "Demo hiring company", now_iso()))

    # Create recruiter user + recruiter record
    cur.execute("""
    INSERT OR IGNORE INTO User(user_id, email, password_hash, role, created_at)
    VALUES (100, ?, ?, 'recruiter', ?)
    """, ("recruiter@talent.co", "hashed", now_iso()))
    cur.execute("""
    INSERT OR IGNORE INTO Recruiters(recruiter_id, user_id, company_id, job_title)
    VALUES (10, 100, 1, 'Technical Recruiter')
    """)

    # Create candidate users + profiles
    cur.execute("""
    INSERT OR IGNORE INTO User(user_id, email, password_hash, role, created_at)
    VALUES (200, ?, ?, 'candidate', ?)
    """, ("cand1@demo.com", "hashed", now_iso()))
    cur.execute("""
    INSERT OR IGNORE INTO UserProfile(user_id, name, dob, photo, is_anonymous)
    VALUES (200, 'Jane Doe', '2002-01-01', NULL, 1)
    """)

    cur.execute("""
    INSERT OR IGNORE INTO User(user_id, email, password_hash, role, created_at)
    VALUES (201, ?, ?, 'candidate', ?)
    """, ("cand2@demo.com", "hashed", now_iso()))
    cur.execute("""
    INSERT OR IGNORE INTO UserProfile(user_id, name, dob, photo, is_anonymous)
    VALUES (201, 'John Smith', '2001-02-02', NULL, 0)
    """)

    # Create roles
    cur.execute("""
    INSERT OR IGNORE INTO JobRoles(role_id, company_id, title, description)
    VALUES (1, 1, 'Backend Engineer (C++)', 'Systems, memory safety, APIs')
    """)
    cur.execute("""
    INSERT OR IGNORE INTO JobRoles(role_id, company_id, title, description)
    VALUES (2, 1, 'Full Stack Engineer', 'React, Node, product work')
    """)

    # Precomputed matches (CandidateJobMatches)
    cur.execute("""
    INSERT OR IGNORE INTO CandidateJobMatches(candidate_id, role_id, match_score, last_updated)
    VALUES (200, 1, 92.0, ?)
    """, (now_iso(),))
    cur.execute("""
    INSERT OR IGNORE INTO CandidateJobMatches(candidate_id, role_id, match_score, last_updated)
    VALUES (201, 2, 84.0, ?)
    """, (now_iso(),))

    conn.commit()
    conn.close()


@app.on_event("startup")
def on_startup():
    init_db()
    seed_demo()


# -----------------------------
# Pydantic models (request/response)
# -----------------------------
class PipelineItem(BaseModel):
    candidate_id: int
    display_name: str
    is_anonymous: bool
    role_id: int
    role_title: str
    match_score: float
    last_updated: str


class InterviewCreateIn(BaseModel):
    candidate_id: int
    role_id: int
    scheduled_time: Optional[str] = Field(
        default=None,
        description="ISO datetime string; for MVP you can pass any string",
    )


class InterviewOut(BaseModel):
    interview_id: int
    candidate_id: int
    recruiter_id: int
    role_id: int
    role_title: str
    scheduled_time: Optional[str]
    status: str


class NoteIn(BaseModel):
    notes: Optional[str] = None
    fit_score: Optional[int] = Field(default=None, ge=1, le=10)
    decision: Optional[str] = Field(default=None, description="advance/reject/pending")


class AvailabilityIn(BaseModel):
    start_time: str
    end_time: str


# -----------------------------
# Helper: verify recruiter belongs to company etc.
# -----------------------------
def get_recruiter_or_404(recruiter_id: int) -> sqlite3.Row:
    conn = db()
    cur = conn.cursor()
    r = cur.execute("SELECT * FROM Recruiters WHERE recruiter_id = ?", (recruiter_id,)).fetchone()
    conn.close()
    if not r:
        raise HTTPException(status_code=404, detail="Recruiter not found")
    return r


# =========================================================
# Recruiter endpoints
# =========================================================

@app.get("/recruiters/{recruiter_id}/pipeline", response_model=List[PipelineItem])
def recruiter_pipeline(recruiter_id: int, role_id: Optional[int] = None):
    """
    Recruiter sees candidate pipeline (matches) for roles in their company.
    """
    recruiter = get_recruiter_or_404(recruiter_id)
    company_id = recruiter["company_id"]

    conn = db()
    cur = conn.cursor()

    params = [company_id]
    role_filter = ""
    if role_id is not None:
        role_filter = "AND jr.role_id = ?"
        params.append(role_id)

    rows = cur.execute(f"""
        SELECT
            m.candidate_id,
            up.name,
            up.is_anonymous,
            m.role_id,
            jr.title AS role_title,
            m.match_score,
            m.last_updated
        FROM CandidateJobMatches m
        JOIN JobRoles jr ON jr.role_id = m.role_id
        LEFT JOIN UserProfile up ON up.user_id = m.candidate_id
        WHERE jr.company_id = ?
        {role_filter}
        ORDER BY m.match_score DESC
        LIMIT 50
    """, params).fetchall()

    conn.close()

    items: List[PipelineItem] = []
    for r in rows:
        anon = bool(r["is_anonymous"]) if r["is_anonymous"] is not None else True
        display_name = f"Anonymous {str(r['candidate_id'])[-4:]}" if anon else (r["name"] or "Candidate")
        items.append(PipelineItem(
            candidate_id=r["candidate_id"],
            display_name=display_name,
            is_anonymous=anon,
            role_id=r["role_id"],
            role_title=r["role_title"],
            match_score=float(r["match_score"]),
            last_updated=r["last_updated"],
        ))
    return items


@app.get("/recruiters/{recruiter_id}/candidates/{candidate_id}")
def recruiter_candidate_detail(recruiter_id: int, candidate_id: int):
    """
    Candidate detail for recruiter.
    IMPORTANT: If candidate is anonymous, we hide name/photo.
    """
    _ = get_recruiter_or_404(recruiter_id)

    conn = db()
    cur = conn.cursor()
    profile = cur.execute("SELECT * FROM UserProfile WHERE user_id = ?", (candidate_id,)).fetchone()
    conn.close()

    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    is_anonymous = bool(profile["is_anonymous"])
    return {
        "candidate_id": candidate_id,
        "isAnonymous": is_anonymous,
        "name": None if is_anonymous else profile["name"],
        "photo": None if is_anonymous else profile["photo"],
        # You can add more safe fields here later (skills, assessments, etc.)
    }


@app.post("/recruiters/{recruiter_id}/interviews", response_model=InterviewOut)
def recruiter_create_interview(recruiter_id: int, payload: InterviewCreateIn):
    """
    Create interview request (or schedule directly if scheduled_time provided).
    """
    recruiter = get_recruiter_or_404(recruiter_id)

    conn = db()
    cur = conn.cursor()

    # Make sure role exists and belongs to recruiter's company
    role = cur.execute("""
        SELECT role_id, title, company_id FROM JobRoles WHERE role_id = ?
    """, (payload.role_id,)).fetchone()
    if not role:
        conn.close()
        raise HTTPException(status_code=404, detail="Role not found")
    if role["company_id"] != recruiter["company_id"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Role does not belong to your company")

    status = "scheduled" if payload.scheduled_time else "requested"

    cur.execute("""
        INSERT INTO Interviews(candidate_id, recruiter_id, role_id, scheduled_time, status)
        VALUES (?, ?, ?, ?, ?)
    """, (payload.candidate_id, recruiter_id, payload.role_id, payload.scheduled_time, status))
    interview_id = cur.lastrowid

    # Notify candidate
    cur.execute("""
        INSERT INTO Notifications(user_id, type, message, is_read, created_at)
        VALUES (?, 'interview', ?, 0, ?)
    """, (payload.candidate_id, f"Interview {status} for role: {role['title']}", now_iso()))

    conn.commit()
    conn.close()

    return InterviewOut(
        interview_id=interview_id,
        candidate_id=payload.candidate_id,
        recruiter_id=recruiter_id,
        role_id=payload.role_id,
        role_title=role["title"],
        scheduled_time=payload.scheduled_time,
        status=status
    )


@app.get("/recruiters/{recruiter_id}/interviews", response_model=List[InterviewOut])
def recruiter_list_interviews(recruiter_id: int):
    recruiter = get_recruiter_or_404(recruiter_id)

    conn = db()
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT i.*, jr.title AS role_title
        FROM Interviews i
        JOIN JobRoles jr ON jr.role_id = i.role_id
        WHERE i.recruiter_id = ?
        ORDER BY COALESCE(i.scheduled_time, i.interview_id) DESC
        LIMIT 100
    """, (recruiter["recruiter_id"],)).fetchall()
    conn.close()

    return [
        InterviewOut(
            interview_id=r["interview_id"],
            candidate_id=r["candidate_id"],
            recruiter_id=r["recruiter_id"],
            role_id=r["role_id"],
            role_title=r["role_title"],
            scheduled_time=r["scheduled_time"],
            status=r["status"],
        )
        for r in rows
    ]


@app.patch("/recruiters/{recruiter_id}/interviews/{interview_id}")
def recruiter_update_interview_status(recruiter_id: int, interview_id: int, status: str):
    """
    Update interview status: requested/scheduled/completed/cancelled
    """
    _ = get_recruiter_or_404(recruiter_id)
    if status not in ("requested", "scheduled", "completed", "cancelled"):
        raise HTTPException(status_code=400, detail="Invalid status")

    conn = db()
    cur = conn.cursor()
    row = cur.execute("""
        SELECT * FROM Interviews WHERE interview_id = ? AND recruiter_id = ?
    """, (interview_id, recruiter_id)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found")

    cur.execute("""
        UPDATE Interviews SET status = ? WHERE interview_id = ?
    """, (status, interview_id))

    # notify candidate
    cur.execute("""
        INSERT INTO Notifications(user_id, type, message, is_read, created_at)
        VALUES (?, 'interview', ?, 0, ?)
    """, (row["candidate_id"], f"Interview status updated to: {status}", now_iso()))

    conn.commit()
    conn.close()
    return {"ok": True, "interview_id": interview_id, "status": status}


@app.post("/recruiters/{recruiter_id}/interviews/{interview_id}/notes")
def recruiter_write_notes(recruiter_id: int, interview_id: int, payload: NoteIn):
    """
    Create or update interview notes for an interview.
    """
    _ = get_recruiter_or_404(recruiter_id)

    conn = db()
    cur = conn.cursor()

    interview = cur.execute("""
        SELECT * FROM Interviews WHERE interview_id = ? AND recruiter_id = ?
    """, (interview_id, recruiter_id)).fetchone()
    if not interview:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found")

    existing = cur.execute("""
        SELECT * FROM InterviewNotes WHERE interview_id = ?
    """, (interview_id,)).fetchone()

    decision = payload.decision
    if decision is not None and decision not in ("advance", "reject", "pending"):
        conn.close()
        raise HTTPException(status_code=400, detail="decision must be advance/reject/pending")

    if existing:
        cur.execute("""
            UPDATE InterviewNotes
            SET notes = COALESCE(?, notes),
                fit_score = COALESCE(?, fit_score),
                decision = COALESCE(?, decision)
            WHERE interview_id = ?
        """, (payload.notes, payload.fit_score, decision, interview_id))
    else:
        cur.execute("""
            INSERT INTO InterviewNotes(interview_id, recruiter_id, notes, fit_score, decision)
            VALUES (?, ?, ?, ?, COALESCE(?, 'pending'))
        """, (interview_id, recruiter_id, payload.notes, payload.fit_score, decision))

    conn.commit()
    conn.close()
    return {"ok": True, "interview_id": interview_id}


@app.post("/recruiters/{recruiter_id}/availability")
def recruiter_add_availability(recruiter_id: int, payload: AvailabilityIn):
    """
    Add an available time slot. (MVP scheduling)
    """
    _ = get_recruiter_or_404(recruiter_id)

    conn = db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO RecruiterAvailability(recruiter_id, start_time, end_time, is_booked)
        VALUES (?, ?, ?, 0)
    """, (recruiter_id, payload.start_time, payload.end_time))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/recruiters/{recruiter_id}/availability")
def recruiter_list_availability(recruiter_id: int):
    _ = get_recruiter_or_404(recruiter_id)

    conn = db()
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT * FROM RecruiterAvailability
        WHERE recruiter_id = ?
        ORDER BY start_time ASC
    """, (recruiter_id,)).fetchall()
    conn.close()

    return [dict(r) for r in rows]


@app.get("/recruiters/{recruiter_id}/notifications")
def recruiter_notifications(recruiter_id: int):
    """
    If you want recruiter notifications, store them on recruiter user_id.
    (Recruiters table maps recruiter_id -> user_id)
    """
    recruiter = get_recruiter_or_404(recruiter_id)
    user_id = recruiter["user_id"]

    conn = db()
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT * FROM Notifications WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 100
    """, (user_id,)).fetchall()
    conn.close()

    return [dict(r) for r in rows]


# -----------------------------
# Run locally
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("recruiter_backend:app", host="127.0.0.1", port=8000, reload=True)

