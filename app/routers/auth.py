"""This module is used to create the user and return the user details."""

from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from jose import jwt, JWTError


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = "4ffd91b79994f1741545df8fd6bdb8a860e2c659be1a47203d656cbb299328a4"
ALGORITHM = "HS256"


bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreatUserRequest(BaseModel):
    """create user request"""

    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    """Token model"""

    access_token: str
    token_type: str


def get_db():
    """This function is used to get the database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbDependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    """This function is used to authenticate the user."""
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt.verify(password, user.hash_password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, role: str, expire_delta: timedelta
):
    """This function is used to create the access token."""
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expire_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
):
    """This function is used to get the current user."""

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="could not validate user",
            )

        return {"username": username, "id": user_id, "role": user_role}
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user"
        ) from exc


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: DbDependency, create_user_request: CreatUserRequest):
    """this function is used to create a user"""
    create_user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hash_password=bcrypt.hash(create_user_request.password),
        is_active=True,
    )
    db.add(create_user_model)
    db.commit()
    return create_user_model


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbDependency
):
    """this function is used to login and get the access token"""
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="could not validate user",
        )

    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=20)
    )

    return {"access_token": token, "token_type": "bearer"}
