## This file starts the FastAPI server and defines the API endpoints.
# It also includes the main logic for handling requests and responses.


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from models import user, product
from routers import auth

## Create the database tables based on the defined SQLAlchemy models.

## Note: For quick assignment development, I used create_all.
#  In production I would use Alembic migrations for version-controlled schema changes.
# Alembic allows you to create migration scripts that can be applied to the database
#  to update the schema without losing data.
Base.metadata.create_all(bind=engine)

## Initialize the FastAPI application and set up CORS middleware to allow requests from the frontend.
app = FastAPI(
    title="PriceIQ API",
    description="Market Intelligence & Pricing Dashboard Backend",
    version="1.0.0",
)

## The CORS middleware is configured to allow requests from http://localhost:3000,
# which is where the frontend will be running during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## The auth router is included in the main FastAPI application, which means that all
#  the endpoints defined in auth.py will be available under the /auth prefix.
app.include_router(auth.router)

@app.get("/")
def root():
    ## This is a simple root endpoint that returns a welcome message.
    #  It can be used to verify that the server is running.
    return {"message": "Welcome to the PriceIQ API!"}
