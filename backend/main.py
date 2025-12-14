# entry point

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.users import router as users_router
from backend.cors_config import add_cors_middleware
import backend.auth, backend.recruiter, backend.assessment
import backend.recruiter_routes
import backend.interviews_routes

from backend.db import engine
from backend.models import Base
from backend.cors_config import add_cors_middleware

# routers
from backend.users import router as users_router
from backend.auth import router as auth_router
from backend.recruiter_routes import router as recruiter_router

# --------------------------------------------------
# CREATE APP FIRST (IMPORTANT)
# --------------------------------------------------

app = FastAPI()

# --------------------------------------------------
# CORS
# --------------------------------------------------

add_cors_middleware(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

Base.metadata.create_all(bind=engine)

# register user routes
app.include_router(users_router)
app.include_router(backend.auth.router)
app.include_router(backend.recruiter_routes.router)
app.include_router(backend.interviews_routes.router)
# app.include_router(recruiter.router)
# app.include_router(assessment.router)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(recruiter_router, prefix="/recruiters")

# optional / demo routes
# app.include_router(assessment_router)

# --------------------------------------------------
# RUN WITH:
# uvicorn main:app --reload
# --------------------------------------------------
