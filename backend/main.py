# entry point
from db import engine
from models import Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from users import router as users_router
from cors_config import add_cors_middleware
import auth, recruiter, assessment


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
app.include_router(auth.router)
# app.include_router(recruiter.router)
# app.include_router(assessment.router)

# to start server: uvicorn main:app --reload