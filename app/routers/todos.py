""" This file is used to create the FastAPI instance and create the database tables. """

from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException, Path
from models import Todos
from database import SessionLocal
from pydantic import BaseModel, Field
from .auth import get_current_user


router = APIRouter()


def get_db():
    """This function is used to get the database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbDependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    """This class is used to validate the request body for the todo creation."""

    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    completed: bool


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: DbDependency):
    """This function is used to get all the todos from the database."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed"
        )

    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def read_one(user: user_dependency, db: DbDependency, todo_id: int = Path(gt=0)):
    """This function is used to get a single todo from the database."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed"
        )
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")


@router.post("/todos", status_code=status.HTTP_201_CREATED)
async def create(user: user_dependency, db: DbDependency, todo_request: TodoRequest):
    """This function is used to create a todo in the database."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed"
        )
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()

    return todo_model


@router.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update(
    user: user_dependency,
    db: DbDependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
    """This function is used to update a todo in the database."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed"
        )
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )

    if todo_model is not None:
        for key, value in todo_request.model_dump().items():
            setattr(todo_model, key, value)
        db.commit()

        return todo_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(user: user_dependency, db: DbDependency, todo_id: int = Path(gt=0)):
    """This function is used to delete a todo from the database."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed"
        )
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is not None:
        db.delete(todo_model)
        db.commit()
        return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")
