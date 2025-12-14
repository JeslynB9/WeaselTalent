from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# =====================================================
# ENUMS
# =====================================================

class InterviewStatus(enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"


class InterviewDecision(enum.Enum):
    advance = "advance"
    reject = "reject"
    pending = "pending"


# =====================================================
# CORE AUTH + USER MANAGEMENT
# =====================================================

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # candidate / recruiter / admin
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    candidate_skills = relationship("CandidateSkillLevel", back_populates="candidate")
    notifications = relationship("Notification", back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    name = Column(String)
    dob = Column(DateTime)
    photo = Column(String)
    is_anonymous = Column(Boolean, default=True)

    user = relationship("User", back_populates="profile")


# =====================================================
# CANDIDATE DOMAIN + SKILLS
# =====================================================

class TechnicalDomain(Base):
    __tablename__ = "technical_domains"

    domain_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

    courses = relationship("Course", back_populates="domain")
    courses = relationship("Course", back_populates="domain")


class CandidateSkillLevel(Base):
    __tablename__ = "candidate_skill_levels"
    __table_args__ = (
        UniqueConstraint("candidate_id", "domain_id"),
    )

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("users.user_id"))
    domain_id = Column(Integer, ForeignKey("technical_domains.domain_id"))
    level = Column(Integer)  # 1–5 or 0–100

    candidate = relationship("User", back_populates="candidate_skills")
    domain = relationship("TechnicalDomain")


# =====================================================
# ASSESSMENTS + TASKS
# =====================================================

## Course scaffold which will be used to feed into AI to generate course 
class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey("technical_domains.domain_id"))
    difficulty_level = Column(Integer)
    description = Column(Text)

    domain = relationship("TechnicalDomain", back_populates="courses")
    assessments = relationship("Assessment", back_populates="course")
    levels = relationship("Level", back_populates="course")
    is_active = Column(Boolean, default=True)


class Assessment(Base):
    __tablename__ = "assessments"

    assessment_id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    generated_at = Column(DateTime, default=datetime.utcnow)
    time_limit_minutes = Column(Integer)
    is_active = Column(Boolean, default=True)

    course = relationship("Course", back_populates="assessments")


class CandidateAssessment(Base):
    __tablename__ = "candidate_assessments"
    __table_args__ = (
        UniqueConstraint("candidate_id", "assessment_id"),
    )
    candidate_assessment_id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("users.user_id"))
    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id"))
    total_score = Column(Integer)
    completed_at = Column(DateTime)


class CandidateTaskProgress(Base):
    __tablename__ = "candidate_task_progress"
    __table_args__ = (
        UniqueConstraint("candidate_id", "task_id"),
    )

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.task_id"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)


class Level(Base):
    __tablename__ = "levels"

    level_id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    name = Column(String)
    order = Column(Integer)

    course = relationship("Course", back_populates="levels")
    tasks = relationship("Task", back_populates="level")


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True)
    level_id = Column(Integer, ForeignKey("levels.level_id"))
    type = Column(String)  # 'content' or 'assessment'
    title = Column(String)
    content = Column(Text)
    order = Column(Integer)

    level = relationship("Level", back_populates="tasks")

class Company(Base):
    __tablename__ = "companies"

    company_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    recruiters = relationship("Recruiter", back_populates="company")
    roles = relationship("JobRole", back_populates="company")


## Recruiter working for company 
class Recruiter(Base):
    __tablename__ = "recruiters"

    recruiter_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    job_title = Column(String)

    company = relationship("Company", back_populates="recruiters")


## Jobs offered by company
class JobRole(Base):
    __tablename__ = "job_roles"

    role_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    title = Column(String)
    description = Column(Text)

    company = relationship("Company", back_populates="roles")
    requirements = relationship(
        "JobRoleRequirement",
        back_populates="role",
        cascade="all, delete-orphan",
    )
    # free-text requirements stored by the web frontend (requirement text + optional level)
    requirements_text = relationship(
        "JobRoleRequirementText",
        back_populates="role",
        cascade="all, delete-orphan",
    )


## Job role requirements in terms of technical domains + skill levels
class JobRoleRequirement(Base):
    __tablename__ = "job_role_requirements"
    __table_args__ = (
        UniqueConstraint("role_id", "domain_id"),
    )

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("job_roles.role_id"))
    domain_id = Column(Integer, ForeignKey("technical_domains.domain_id"))
    minimum_level = Column(Integer)

    role = relationship("JobRole", back_populates="requirements")
    domain = relationship("TechnicalDomain")


class JobRoleRequirementText(Base):
    """Simple free-text requirements storage for the frontend form.

    This stores arbitrary requirement text and an optional numeric level.
    It keeps the frontend UX working without forcing a domain->id mapping.
    """
    __tablename__ = "job_role_requirements_text"

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("job_roles.role_id"), nullable=False)
    requirement_text = Column(Text)
    level = Column(Integer, nullable=True)

    role = relationship("JobRole", back_populates="requirements_text")


# =====================================================
# MATCHING SYSTEM
# =====================================================

## Match candidate to job with match score 
class CandidateJobMatch(Base):
    __tablename__ = "candidate_job_matches"
    __table_args__ = (
        UniqueConstraint("candidate_id", "role_id"),
    )

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("users.user_id"))
    role_id = Column(Integer, ForeignKey("job_roles.role_id"))
    match_score = Column(Integer)
    last_updated = Column(DateTime, default=datetime.utcnow)


# =====================================================
# INTERVIEW PROCESS
# =====================================================

class RecruiterAvailability(Base):
    __tablename__ = "recruiter_availability"

    availability_id = Column(Integer, primary_key=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.recruiter_id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_booked = Column(Boolean, default=False)



## Interview scheduled between candidate and recruite
class Interview(Base):
    __tablename__ = "interviews"

    interview_id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("users.user_id"))
    recruiter_id = Column(Integer, ForeignKey("recruiters.recruiter_id"))
    role_id = Column(Integer, ForeignKey("job_roles.role_id"))
    scheduled_time = Column(DateTime)
    status = Column(Enum(InterviewStatus))


## Notes by recruiter after interview
class InterviewNote(Base):
    __tablename__ = "interview_notes"

    id = Column(Integer, primary_key=True)
    interview_id = Column(Integer, ForeignKey("interviews.interview_id"))
    recruiter_id = Column(Integer, ForeignKey("recruiters.recruiter_id"))
    notes = Column(Text)
    fit_score = Column(Integer)
    decision = Column(Enum(InterviewDecision))


# =====================================================
# NOTIFICATIONS
# =====================================================

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    type = Column(String)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")

