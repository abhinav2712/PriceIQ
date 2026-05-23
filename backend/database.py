## This file connects to PostgreSQL database and creates tables if they don't exist.

## I use SQLAlchemy sessions per request. 
# The get_db dependency opens a session, yields it to the endpoint, and closes it after the request finishes.

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

## The DATABASE_URL should be in the format: postgresql://user:password@host:port/dbname
## The engine is created using SQLAlchemy's create_engine function, which establishes the connection to the database.
engine = create_engine(DATABASE_URL)

## The SessionLocal class is a factory for creating new database sessions.
# It is configured to not autocommit and not autoflush, and it binds to the engine we created.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

## The Base class is the base class for all our database models. It is created using SQLAlchemy's declarative_base function,
# which allows us to define our models as Python classes that are mapped to database tables.
Base= declarative_base()

## The get_db function is a dependency that can be used in FastAPI routes to get a database session.
def get_db():
    db = SessionLocal()
    try:
        ## The yield statement allows us to use this function as a context manager,
        # ensuring that the database session is properly closed after the request is handled.
        yield db
    finally:
        db.close()
