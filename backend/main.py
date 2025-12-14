# entry point
from backend.db import engine
from backend.models import Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.users import router as users_router
from backend.cors_config import add_cors_middleware
import backend.auth, backend.recruiter, backend.assessment
import backend.recruiter_routes
import backend.interviews_routes


app = FastAPI()
add_cors_middleware(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create all tables defined on `Base`
Base.metadata.create_all(bind=engine)

# register user routes
app.include_router(users_router)
app.include_router(backend.auth.router)
app.include_router(backend.recruiter_routes.router)
app.include_router(backend.interviews_routes.router)
# app.include_router(recruiter.router)
# app.include_router(assessment.router)

# to start server: uvicorn main:app --reload