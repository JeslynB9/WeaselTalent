# entry point

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db import engine
from backend.models import Base
from backend.cors_config import add_cors_middleware

# routers
from backend.users import router as users_router
from backend.auth import router as auth_router
from backend.recruiter_routes import router as recruiter_router
from backend.assessment import router as assessment_router  # optional

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

# --------------------------------------------------
# ROUTERS (INCLUDE ONCE)
# --------------------------------------------------

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(recruiter_router, prefix="/recruiters")

# optional / demo routes
# app.include_router(assessment_router)

# --------------------------------------------------
# RUN WITH:
# uvicorn main:app --reload
# --------------------------------------------------
