# for sqlite3 connection 

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# use URL from .env if exists; else 
DATABASE_URL = os.getenv (
    "DATABASE_URL",
    "sqlite:///./app.db"
)

# the actual db connection
engine = create_engine (
    DATABASE_URL,
    connect_args = {"check_same_thread": False}
)

# routes to db
SessionLocal = sessionmaker (
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()