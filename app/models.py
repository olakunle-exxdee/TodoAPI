""" This file contains the database schema for the todo app. """

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Users(Base):
    """This class represents the user table in the database."""

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hash_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)


class Todos(Base):
    """This class represents the todos table in the database."""

    __tablename__ = "todos"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    title = Column(String, index=True)
    description = Column(String)
    priority = Column(Integer)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
