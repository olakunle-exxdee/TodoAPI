from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException, Path
from models import Todos
from database import SessionLocal
from .auth import get_current_user


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


def get_db():
    """This function is used to get the database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbDependency = Annotated[Session, Depends(get_db)]
UserDependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todos", status_code=status.HTTP_200_OK)
def get_all_todos(db: DbDependency, user: UserDependency):
    """This function is used to get all the todos."""
    if user is None or user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    return db.query(Todos).all()


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: UserDependency,
    db: DbDependency,
    todo_id: int = Path(..., title="The ID of the todo to delete", gt=0),
):
    """This function is used to delete a todo."""
    if user is None or user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    db.delete(todo_model)
    db.commit()
