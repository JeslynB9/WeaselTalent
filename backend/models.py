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

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


# Defines what /assessments returns
class AssessmentOut(BaseModel): 
    id: str
    track: str
    level: int
    title: str
    prompt: str
    rubric: Dict[str, Any]

# Defines what frontend must send when submitting: score, feedback, timestamp)
class SubmissionIn(BaseModel): 
    candidate_id: str = Field(..., min_length=1, description="Anonymous candidate identifier, e.g., cand-0001")
    assessment_id: str = Field(..., min_length=1)
    answer_text: str = Field(..., min_length=10, description="Candidate response (text or pasted code).")

# Defines what backend returns after submission:
class SubmissionOut(BaseModel): 
    id: int
    candidate_id: str
    assessment_id: str
    answer_text: str
    score: Optional[int] = None
    feedback: Optional[str] = None
    created_at: str
