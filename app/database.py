""" Database configuration"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

if os.getenv("DEPLOYMENT_ENVIRONMENT") == "DEV":
    engine = create_engine(
        os.getenv("DB_URL"), connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(os.getenv("DB_URL"))




SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
