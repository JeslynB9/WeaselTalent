from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
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

def seed_assessments() -> None: #sampling assessments for frontend
  



