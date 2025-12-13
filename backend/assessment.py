from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from models import AssessmentOut, SubmissionIn, SubmissionOut


DB_PATH = "assessments.db" #SQLite database file
app = FastAPI(title="Lyrathon Assessments Backend", version="0.1.0") #FastAPI now listens for HTTP requests

# ----------------------------
# Database helpers
# ----------------------------
def db() -> sqlite3.Connection:  #connecting to database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None: # creating tables
    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS assessments (
            id TEXT PRIMARY KEY,
            track TEXT NOT NULL,
            level INTEGER NOT NULL,
            title TEXT NOT NULL,
            prompt TEXT NOT NULL,
            rubric_json TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id TEXT NOT NULL,
            assessment_id TEXT NOT NULL,
            answer_text TEXT NOT NULL,
            score INTEGER,
            feedback TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(candidate_id, assessment_id),
            FOREIGN KEY(assessment_id) REFERENCES assessments(id)
        )
        """
    )

    conn.commit()
    conn.close()

def seed_assessments() -> None: # sample assessments so frontend has data immediately
    """Seed a few assessments if none exist."""
    conn = db()
    cur = conn.cursor()

    count = cur.execute("SELECT COUNT(*) AS c FROM assessments").fetchone()["c"]# assessments already exist, don’t add again
    if count > 0:
        conn.close()
        return

    seeds = [
        (
            "py-l1",
            "Python",
            1,
            "Python Basics: Clean Input",
            "Write a short explanation of how you would validate user input for a Python CLI tool. Mention edge cases.",
            json.dumps(
                {
                    "criteria": [
                        {"name": "clarity", "weight": 0.25},
                        {"name": "edge_cases", "weight": 0.35},
                        {"name": "practicality", "weight": 0.40},
                    ]
                }
            ),
        ),
        (
            "py-l2",
            "Python",
            2,
            "Python Data: Simple Analysis",
            "Explain how you would compute average, median, and detect outliers in a list of numbers. Provide pseudocode.",
            json.dumps(
                {
                    "criteria": [
                        {"name": "correctness", "weight": 0.45},
                        {"name": "structure", "weight": 0.25},
                        {"name": "outliers", "weight": 0.30},
                    ]
                }
            ),
        ),
        (
            "cpp-l1",
            "Backend C++",
            1,
            "C++ Memory Safety",
            "Explain two common memory safety bugs in C++ and how you would prevent them in production code.",
            json.dumps(
                {
                    "criteria": [
                        {"name": "understanding", "weight": 0.50},
                        {"name": "prevention", "weight": 0.50},
                    ]
                }
            ),
        ),
    ]

    cur.executemany(
        "INSERT INTO assessments (id, track, level, title, prompt, rubric_json) VALUES (?, ?, ?, ?, ?, ?)",
        seeds,
    )
    conn.commit()
    conn.close()




# ----------------------------
# Scoring (simple + explainable)
# ----------------------------
def simple_score(assessment_track: str, answer_text: str) -> tuple[int, str]: # scoring algorithm
    """
    Hackathon-friendly scoring:
    - length + keyword coverage
    - produces score 0–100 and short feedback
    Replace this later with AI/rubric scoring if you want.
    """
    text = answer_text.lower().strip()
    length = len(text)

    # Base from length (cap) - capped at 50 
    base = min(50, int(length / 12))  # ~600 chars => 50

    # Track-specific keywords
    keywords = {
        "python": ["validate", "edge", "exception", "type", "test", "input"],
        "backend c++": ["pointer", "memory", "leak", "raii", "smart", "buffer", "overflow"],
    }
    track_key = assessment_track.lower()
    pool = keywords.get(track_key, ["explain", "example", "tradeoff"])

    hits = sum(1 for k in pool if k in text)
    kw_score = min(40, hits * 8)  # max 40

    # Bonus for structure - dont know if i should include this
    bonus = 0
    if "\n" in answer_text:
        bonus += 5
    if any(bullet in answer_text for bullet in ["- ", "* ", "1)", "2)"]):
        bonus += 5

    score = max(0, min(100, base + kw_score + bonus)) # final score should be between 0 to 100)

    feedback_parts = []
    if score < 50:
        feedback_parts.append("Add more detail and include concrete edge cases/examples.")
    if hits == 0:
        feedback_parts.append("Try using more role-specific terminology to show depth.")
    if bonus == 0:
        feedback_parts.append("Use bullet points or short sections for readability.")
    if not feedback_parts:
        feedback_parts.append("Strong response. Clear, structured, and role-relevant.")

    return score, " ".join(feedback_parts)


# ----------------------------
# Startup
# ----------------------------
@app.on_event("startup")
def startup() -> None: # runs once when server starts
    init_db()
    seed_assessments() # ensures database and assessments exists


# ----------------------------
# Routes
# ----------------------------
@app.get("/assessments", response_model=List[AssessmentOut]) # Frontend calls this to list assessments
def list_assessments(track: Optional[str] = None) -> List[AssessmentOut]:
    conn = db()
    cur = conn.cursor()

    if track:
        rows = cur.execute(
            "SELECT * FROM assessments WHERE track = ? ORDER BY level ASC",
            (track,),
        ).fetchall()
    else:
        rows = cur.execute(
            "SELECT * FROM assessments ORDER BY track ASC, level ASC"
        ).fetchall()

    conn.close()

    out: List[AssessmentOut] = []
    for r in rows:
        out.append(
            AssessmentOut(
                id=r["id"],
                track=r["track"],
                level=r["level"],
                title=r["title"],
                prompt=r["prompt"],
                rubric=json.loads(r["rubric_json"]),
            )
        )
    return out


@app.get("/assessments/{assessment_id}", response_model=AssessmentOut)
def get_assessment(assessment_id: str) -> AssessmentOut:
    conn = db()
    cur = conn.cursor()
    r = cur.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,)).fetchone()
    conn.close()

    if not r:
        raise HTTPException(status_code=404, detail=f"Assessment '{assessment_id}' not found.")

    return AssessmentOut(
        id=r["id"],
        track=r["track"],
        level=r["level"],
        title=r["title"],
        prompt=r["prompt"],
        rubric=json.loads(r["rubric_json"]),
    )


@app.post("/submissions", response_model=SubmissionOut)
def submit_assessment(payload: SubmissionIn) -> SubmissionOut:
    # Validate assessment exists
    conn = db()
    cur = conn.cursor()
    a = cur.execute("SELECT * FROM assessments WHERE id = ?", (payload.assessment_id,)).fetchone()
    if not a:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Assessment '{payload.assessment_id}' not found.")

    # Score it
    score, feedback = simple_score(a["track"], payload.answer_text)
    now = datetime.now(timezone.utc).isoformat()

    try:
        cur.execute(
            """
            INSERT INTO submissions (candidate_id, assessment_id, answer_text, score, feedback, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (payload.candidate_id, payload.assessment_id, payload.answer_text, score, feedback, now),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(
            status_code=409,
            detail="You already submitted this assessment. (candidate_id + assessment_id must be unique)",
        )

    sub_id = cur.lastrowid
    conn.close()

    return SubmissionOut(
        id=sub_id,
        candidate_id=payload.candidate_id,
        assessment_id=payload.assessment_id,
        answer_text=payload.answer_text,
        score=score,
        feedback=feedback,
        created_at=now,
    )


@app.get("/candidates/{candidate_id}/submissions", response_model=List[SubmissionOut]) # Allows:, candidate dashboard & recruiter review
def list_candidate_submissions(candidate_id: str) -> List[SubmissionOut]:
    conn = db()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT * FROM submissions WHERE candidate_id = ? ORDER BY created_at DESC",
        (candidate_id,),
    ).fetchall()
    conn.close()

    return [
        SubmissionOut(
            id=r["id"],
            candidate_id=r["candidate_id"],
            assessment_id=r["assessment_id"],
            answer_text=r["answer_text"],
            score=r["score"],
            feedback=r["feedback"],
            created_at=r["created_at"],
        )
        for r in rows
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)



