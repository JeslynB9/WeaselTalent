# define tables

### CORE AUTH + USER MANAGEMENT
    # User: user_id, email, password_hash, role, created_at, last_login, is_active
    # UserProfile: user_id, name, dob, photo, is_anonymous

### CANDIDATE DOMAIN + SKILLS 
    # TechnicalDomains: domain_id, name, description 
    # CandidateSkillLevels: candidate_id (aka user_id)

### ASSESSMENTS + TASKS
    # Assessments: assessment_id, scaffold_id, generated_at, time_limit_minutes, is_active
    # AssessmentScaffolds: scaffold_id, domain_id, difficulty_level, description 
    # Tasks: task_id, assessment_id, task_type, prompt
    # CandidateAssessments: candidate_assesment_id, candidate_id, assessment_id, total_score, completed_at
    # CandidateTaskResults: candidate_assessment_id, task_id, score, answer

### COMPANIES + ROLES
    # Companies: company_id, name, description, created_at
    # Recruiters: recruiter_id, company_id, job_title
    # JobRoles: role_id, company_id, title, description
    # JobRoleRequirements: role_id, domain_id, minimum_level

### MATCHING SYSTEM
    # CandidateJobMatches: candidate_id, role_id, match_score, last_updated                # to be recomputed when candidate finishes assessment, job requirements change 

### INTERVIEW PROCESS
    # RecruiterAvailability: availability_id, recruiter_id, start_time, end_time, is_booked
    # Interviews: interview_id, candidate_id, recruiter_id, role_id, scheduled_time, status ENUM('scheduled','completed','cancelled')
    # InterviewNotes: interview_id, recruiter_id, notes, fit_score, decision ENUM('advance','reject','pending')

### NOTIFICATIONS
    # Notifications: notification_id, user_id, type, message, is_read, created_at 

from sqlalchemy import (
    Column, 
    Integer,
    String, 
    Boolean, 
    DateTime,
)

from datetime import datetime, timezone
from db import Base

## Users table
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)

    created_at = Column (
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    last_login = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

## Assessment table
class Assessment(Base):
    __tablename__ = "assessments"

    assessment_id = Column(Integer, primary_key=True, index=True)
    # scaffold that will be used to create the assessment
    scaffold_id = Column(Integer, nullable=False)
    generated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    time_limit_minutes = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)