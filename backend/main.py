# entry point
from db import engine
from models import Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from users import router as users_router
from candidate import router as candidate_router
from auth import router as auth_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register signup for candidate routes
app.include_router(candidate_router)

# create all tables defined on `Base`
Base.metadata.create_all(bind=engine)

# register user routes
app.include_router(users_router)

## register login auth routes
app.include_router(auth_router)

# to start server: uvicorn main:app --reload