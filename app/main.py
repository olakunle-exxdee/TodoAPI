"""This file is used to create the FastAPI instance and create the database tables."""

from fastapi import FastAPI

import app.models as models
from app.database import engine
from app.routers import admin, auth, todos, user

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    """This function is used to check the health of the application."""
    return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)
