from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from db import SessionLocal
from models import (
    Course,
    Level,
    Task,
    Assessment,
    CandidateAssessment,
    CandidateTaskProgress,
)

from pydantic import BaseModel

# -----------------------------
# DB dependency
# -----------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Response Schemas
# -----------------------------

class TaskOut(BaseModel):
    task_id: int
    type: str
    title: str
    content: str
    order: int
    completed: bool
    unlocked: bool


class LevelOut(BaseModel):
    level_id: int
    name: str
    order: int
    tasks: List[TaskOut]


class AssessmentDetailOut(BaseModel):
    assessment_id: int
    time_limit_minutes: int
    levels: List[LevelOut]


class CourseListOut(BaseModel):
    course_id: int
    description: str
    difficulty_level: int
    time_limit_minutes: int
    is_completed: bool
    score: int | None


class TaskCompleteIn(BaseModel):
    candidate_id: int
    task_id: int

# -----------------------------
# Router
# -----------------------------

router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)

# -----------------------------
# Helper logic
# -----------------------------

def compute_task_unlocked(task, level_tasks, completed_task_ids, level_unlocked):
    if not level_unlocked:
        return False

    if task.order == 1:
        return True

    previous_tasks = [t for t in level_tasks if t.order < task.order]

    if task.type == "content":
        prev_task = max(previous_tasks, key=lambda t: t.order)
        return prev_task.task_id in completed_task_ids

    if task.type == "assessment":
        required_lessons = [
            t.task_id for t in previous_tasks if t.type == "content"
        ]
        return all(tid in completed_task_ids for tid in required_lessons)

    return False

# -----------------------------
# Routes
# -----------------------------

@router.get("/", response_model=List[CourseListOut])
def list_courses(candidate_id: int = Query(...), db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    result = []

    completed_assessments = {
        ca.assessment_id: ca
        for ca in db.query(CandidateAssessment)
        .filter(CandidateAssessment.candidate_id == candidate_id)
        .all()
    }

    for course in courses:
        assessment = (
            db.query(Assessment)
            .filter(Assessment.course_id == course.course_id)
            .first()
        )

        completed = False
        score = None

        if assessment and assessment.assessment_id in completed_assessments:
            completed = True
            score = completed_assessments[assessment.assessment_id].total_score

        result.append(CourseListOut(
            course_id=course.course_id,
            description=course.description,
            difficulty_level=course.difficulty_level,
            time_limit_minutes=assessment.time_limit_minutes if assessment else 60,
            is_completed=completed,
            score=score
        ))

    return result


@router.get("/{course_id}", response_model=AssessmentDetailOut)
def get_course_detail(
    course_id: int,
    candidate_id: int = Query(...),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    completed_task_ids = {
        p.task_id
        for p in db.query(CandidateTaskProgress)
        .filter(CandidateTaskProgress.candidate_id == candidate_id)
        .all()
    }

    completed_assessment_levels = set()
    completed_assessments = (
        db.query(CandidateAssessment)
        .filter(CandidateAssessment.candidate_id == candidate_id)
        .all()
    )

    for ca in completed_assessments:
        task = db.query(Task).filter(Task.task_id == ca.assessment_id).first()
        if task:
            completed_assessment_levels.add(task.level_id)

    levels_out = []
    sorted_levels = sorted(course.levels, key=lambda l: l.order)

    for idx, level in enumerate(sorted_levels):
        if level.order == 1:
            level_unlocked = True
        else:
            prev_level = sorted_levels[idx - 1]
            level_unlocked = prev_level.level_id in completed_assessment_levels

        tasks_out = []
        sorted_tasks = sorted(level.tasks, key=lambda t: t.order)

        for task in sorted_tasks:
            unlocked = compute_task_unlocked(
                task,
                sorted_tasks,
                completed_task_ids,
                level_unlocked
            )

            tasks_out.append(TaskOut(
                task_id=task.task_id,
                type=task.type,
                title=task.title,
                content=task.content,
                order=task.order,
                completed=task.task_id in completed_task_ids,
                unlocked=unlocked
            ))

        levels_out.append(LevelOut(
            level_id=level.level_id,
            name=level.name,
            order=level.order,
            tasks=tasks_out
        ))

    assessment = (
        db.query(Assessment)
        .filter(Assessment.course_id == course.course_id)
        .first()
    )

    return AssessmentDetailOut(
        assessment_id=assessment.assessment_id if assessment else course.course_id,
        time_limit_minutes=assessment.time_limit_minutes if assessment else 60,
        levels=levels_out
    )


@router.post("/tasks/complete")
def complete_task(data: TaskCompleteIn, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == data.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.type != "content":
        raise HTTPException(status_code=400, detail="Only content tasks allowed")

    existing = db.query(CandidateTaskProgress).filter(
        CandidateTaskProgress.candidate_id == data.candidate_id,
        CandidateTaskProgress.task_id == data.task_id
    ).first()

    if existing:
        return {"status": "already_completed"}

    progress = CandidateTaskProgress(
        candidate_id=data.candidate_id,
        task_id=data.task_id,
        completed_at=datetime.utcnow()
    )

    db.add(progress)
    db.commit()

    return {"status": "completed"}

@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task.task_id,
        "title": task.title,
        "content": task.content,
        "type": task.type
    }
