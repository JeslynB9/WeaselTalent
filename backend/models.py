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

from proto import ENUM
from sqlalchemy import (
    Column, 
    Integer,
    String, 
    Boolean, 
    DateTime,
)

from datetime import datetime, timezone
from db import Base

### Users table
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

## Users profile (personal info)
class UserProfile(Base): 
    __tablename__ = "user_profiles"
    user_id = Column(Integer, primary_key=True, index=True)  
    full_name = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    profile_photo_url = Column(String, nullable=True)
    is_anonymous = Column(Boolean, default=False, nullable=False)

## Users saved preferences
class UserPreferences(Base):
    __tablename__ = "user_preferences" 
    user_id = Column(Integer, primary_key=True, index=True)
    preferred_technical_domains = Column(Integer, primary_key=True)

## Technical domains (e.g. web dev, backend, data science, etc) 
class TechnicalDomains(Base): 
    __tablename__ = "technical_domains" 
    domain_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

## domains candidate is skilled in (they did assessment to skill up)
class CandidateDomains(Base): 
    __tablename__ = "candidate_domains"
    candidate_id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, primary_key=True, index=True)
    skill_level = Column(Integer, nullable=False)  


### Assessment table
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

class AssessmentScaffold(Base):
    __tablename__ = "assessment_scaffolds"
    scaffold_id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, nullable=False)
    difficulty_level = Column(String, nullable=False)
    description = Column(String, nullable=True)


class Task(Base):
    __tablename__ = "tasks"
    task_id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, nullable=False)
    task_type = Column(String, nullable=False)  
    prompt = Column(String, nullable=False)
    max_score = Column(Integer, nullable=False)

class CandidateAssessment(Base):
    __tablename__ = "candidate_assessments"
    candidate_assessment_id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, nullable=False)
    assessment_id = Column(Integer, nullable=False)
    total_score = Column(Integer, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class CandidateTaskResult(Base):
    __tablename__ = "candidate_task_results"
    candidate_assessment_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, primary_key=True, index=True)
    score = Column(Integer, nullable=True)
    answer = Column(String, nullable=True)

class Company(Base):
    __tablename__ = "companies"
    company_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

class Recruiter(Base):
    __tablename__ = "recruiters"
    recruiter_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False)
    job_title = Column(String, nullable=False)

class JobRole(Base):
    __tablename__ = "job_roles"
    role_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True) 

class JobRoleRequirement(Base):
    __tablename__ = "job_role_requirements"
    role_id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, primary_key=True, index=True)
    minimum_level = Column(Integer, nullable=False)

class CandidateJobMatch(Base):
    __tablename__ = "candidate_job_matches"
    candidate_id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, primary_key=True, index=True)
    match_score = Column(Integer, nullable=False)
    last_updated = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

class RecruiterAvailability(Base):
    __tablename__ = "recruiter_availability"
    availability_id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    is_booked = Column(Boolean, default=False, nullable=False)

class Interview(Base):
    __tablename__ = "interviews"
    interview_id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, nullable=False)
    recruiter_id = Column(Integer, nullable=False)
    role_id = Column(Integer, nullable=False)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(ENUM('scheduled','completed','cancelled'), default='scheduled', nullable=False)

class InterviewNote(Base):
    __tablename__ = "interview_notes"
    interview_id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)
    fit_score = Column(Integer, nullable=True)
    decision = Column(ENUM('advance','reject','pending'), default='pending', nullable=False)

class Notification(Base):
    __tablename__ = "notifications"
    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )