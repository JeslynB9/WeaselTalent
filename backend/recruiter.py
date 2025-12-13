# recruiter functions
# =========================
# IMPORTS
# =========================
import json
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# =========================
# APP + DATABASE
# =========================
DB_PATH = "lyrathon.db"
app = FastAPI(title="Lyrathon Backend", version="1.0")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# DATABASE INITIALISATION
# =========================
def init_db():
    conn = db()
    cur = conn.cursor()

    # Candidates (anonymous-safe)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id TEXT PRIMARY KEY,
        is_anonymous INTEGER NOT NULL,
        name TEXT,
        title TEXT,
        bio TEXT
    )
    """)

    # Assessments
    cur.execute("""
    CREATE TABLE IF NOT EXISTS assessments (
        id TEXT PRIMARY KEY,
        track TEXT NOT NULL,
        level INTEGER NOT NULL,
        title TEXT NOT NULL,
        prompt TEXT NOT NULL
    )
    """)

    # Submissions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT NOT NULL,
        assessment_id TEXT NOT NULL,
        answer_text TEXT NOT NULL,
        score INTEGER,
        feedback TEXT,
        created_at TEXT,
        UNIQUE(candidate_id, assessment_id)
    )
    """)

    # Recruiter matches
    cur.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT NOT NULL,
        match_score INTEGER NOT NULL,
        reason TEXT
    )
    """)

    # Interviews
    cur.execute("""
    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT NOT NULL,
        status TEXT NOT NULL,
        scheduled_time TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================
# SEED DATA (DEMO READY)
# =========================
def seed_data():
    conn = db()
    cur = conn.cursor()

    # Candidates
    cur.execute("""
    INSERT OR IGNORE INTO candidates VALUES
    ('cand-0001', 1, 'Jane Doe', 'Backend Engineer', 'C++ systems engineer'),
    ('cand-0002', 0, 'John Smith', 'Full Stack Developer', 'React + Node developer')
    """)

    # Assessments
    cur.execute("""
    INSERT OR IGNORE INTO assessments VALUES
    ('py-l1', 'Python', 1, 'Python Basics',
     'Explain how you validate user input and handle edge cases in Python.'),
    ('cpp-l1', 'Backend C++', 1, 'C++ Memory Safety',
     'Explain two common C++ memory bugs and how to prevent them.')
    """)

    # Matches
    cur.execute("""
    INSERT OR IGNORE INTO matches (candidate_id, match_score, reason) VALUES
    ('cand-0001', 92, 'Strong systems knowledge and memory safety'),
    ('cand-0002', 84, 'Good balance of frontend and backend skills')
    """)

    conn.commit()
    conn.close()


# =========================
# SCORING LOGIC
# =========================
def score_answer(track: str, answer: str):
    text = answer.lower()
    base = min(50, len(answer) // 12)

    keywords = {
        "python": ["validate", "exception", "edge", "test"],
        "backend c++": ["pointer", "memory", "leak", "raii", "overflow"]
    }

    hits = sum(1 for k in keywords.get(track.lower(), []) if k in text)
    keyword_score = min(40, hits * 8)

    bonus = 10 if "\n" in answer else 0

    score = min(100, base + keyword_score + bonus)

    feedback = "Strong response."
    if score < 60:
        feedback = "Needs more depth and domain-specific reasoning."

    return score, feedback


# =========================
# API MODELS
# =========================
class SubmissionIn(BaseModel):
    candidate_id: str
    assessment_id: str
    answer_text: str = Field(..., min_length=10)


# =========================
# STARTUP
# =========================
@app.on_event("startup")
def startup():
    init_db()
    seed_data()


# =========================
# ASSESSMENTS
# =========================
@app.get("/assessments")
def list_assessments():
    conn = db()
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM assessments").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/submissions")
def submit_assessment(payload: SubmissionIn):
    conn = db()
    cur = conn.cursor()

    a = cur.execute(
        "SELECT * FROM assessments WHERE id = ?",
        (payload.assessment_id,)
    ).fetchone()

    if not a:
        raise HTTPException(404, "Assessment not found")

    score, feedback = score_answer(a["track"], payload.answer_text)
    now = datetime.now(timezone.utc).isoformat()

    try:
        cur.execute("""
        INSERT INTO submissions
        (candidate_id, assessment_id, answer_text, score, feedback, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            payload.candidate_id,
            payload.assessment_id,
            payload.answer_text,
            score,
            feedback,
            now
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Assessment already submitted")

    conn.close()

    return {
        "candidate_id": payload.candidate_id,
        "assessment_id": payload.assessment_id,
        "score": score,
        "feedback": feedback
    }


# =========================
# RECRUITER PIPELINE
# =========================
@app.get("/recruiter/candidates")
def recruiter_candidates():
    conn = db()
    cur = conn.cursor()

    rows = cur.execute("""
    SELECT c.id, c.is_anonymous, c.name, c.title,
           m.match_score, m.reason
    FROM candidates c
    JOIN matches m ON c.id = m.candidate_id
    ORDER BY m.match_score DESC
    """).fetchall()

    conn.close()

    return [{
        "id": r["id"],
        "name": None if r["is_anonymous"] else r["name"],
        "isAnonymous": bool(r["is_anonymous"]),
        "title": r["title"],
        "matchScore": r["match_score"],
        "reason": r["reason"]
    } for r in rows]


@app.get("/recruiter/candidates/{candidate_id}")
def recruiter_candidate_detail(candidate_id: str):
    conn = db()
    cur = conn.cursor()

    c = cur.execute(
        "SELECT * FROM candidates WHERE id = ?",
        (candidate_id,)
    ).fetchone()

    if not c:
        raise HTTPException(404, "Candidate not found")

    conn.close()

    return {
        "id": c["id"],
        "name": None if c["is_anonymous"] else c["name"],
        "isAnonymous": bool(c["is_anonymous"]),
        "title": c["title"],
        "bio": c["bio"]
    }


# =========================
# INTERVIEWS
# =========================
@app.post("/recruiter/interviews")
def schedule_interview(candidate_id: str, time: str):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO interviews (candidate_id, status, scheduled_time)
    VALUES (?, 'scheduled', ?)
    """, (candidate_id, time))

    conn.commit()
    conn.close()

    return {
        "candidate_id": candidate_id,
        "status": "scheduled",
        "time": time
    }


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
