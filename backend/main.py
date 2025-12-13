# entry point
from db import engine
from models import Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from users import router as users_router

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

# to start server: uvicorn main:app --reload