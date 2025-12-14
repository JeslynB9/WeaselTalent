# entry point
from backend.db import engine
from backend.models import Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.users import router as users_router
from backend.recruiter_routes import router as recruiter_router

app = FastAPI()

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
app.include_router(recruiter_router)

# to start server: uvicorn main:app --reload