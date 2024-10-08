""" This file is used to create the FastAPI instance and create the database tables. """

from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from app.models import Users
from app.database import SessionLocal
from .auth import get_current_user


router = APIRouter(
    prefix="/user",
    tags=["user"],
)

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    """This function is used to get the database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbDependency = Annotated[Session, Depends(get_db)]
UserDependency = Annotated[dict, Depends(get_current_user)]


class UserVerification(BaseModel):
    """This class is used to validate the request body for the user verification."""

    password: str
    new_password: str = Field(min_length=6)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_current_user(user: UserDependency, db: DbDependency):
    """This function is used to get the current user."""

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed"
        )

    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put("/update_password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(
    user: UserDependency, db: DbDependency, user_verification: UserVerification
):
    """this function is used to update_password"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed"
        )
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt.verify(user_verification.password, user_model.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    user_model.hash_password = bcrypt.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    return {"message": "Password updated successfully"}
