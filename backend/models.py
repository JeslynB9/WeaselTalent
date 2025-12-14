# define tables

### CORE AUTH + USER MANAGEMENT
    # User: user_id, email, password_hash, role, created_at, last_login, is_active
    # UserProfile: user_id, name, dob, photo, is_anonymous

### CANDIDATE DOMAIN + SKILLS 
    # TechnicalDomains: domain_id, name, description 
    # CandidateSkillLevels: candidate_id (aka user_id)

### ASSESSMENTS
    # Assessments: assessment_id, scaffold_id, generated_at, time_limit_minutes, is_active
    # AssessmentScaffolds: scaffold_id, domain_id, difficulty_level, description 
    # CandidateAssessments: candidate_assesment_id, candidate_id, assessment_id, total_score, completed_at

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

    scaffolds = relationship("AssessmentScaffold", back_populates="domain")


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

## Assessment scaffold whihc will be used to feed into AI to generate assessment 
class AssessmentScaffold(Base):
    __tablename__ = "assessment_scaffolds"

    scaffold_id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey("technical_domains.domain_id"))
    difficulty_level = Column(Integer)
    description = Column(Text)

    domain = relationship("TechnicalDomain", back_populates="scaffolds")
    assessments = relationship("Assessment", back_populates="scaffold")


class Assessment(Base):
    __tablename__ = "assessments"

    assessment_id = Column(Integer, primary_key=True)
    scaffold_id = Column(Integer, ForeignKey("assessment_scaffolds.scaffold_id"))
    generated_at = Column(DateTime, default=datetime.utcnow)
    time_limit_minutes = Column(Integer)
    is_active = Column(Boolean, default=True)

    scaffold = relationship("AssessmentScaffold", back_populates="assessments")
    # tasks relationship removed: Task model is not defined in this codebase yet.
    # If you add Task later, restore the relationship:
    # tasks = relationship("Task", back_populates="assessment")

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
    # task_results relationship removed: CandidateTaskResult not defined here.
    # Add it back if you define CandidateTaskResult model.

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
