from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.models import Base  # Assuming Task is one of your models
from os import path, getcwd


def relative_path_backend():
    """Determines the relative path to the database file, prioritizing 'backend/db.sqlite3'."""
    return path.abspath(path.join(getcwd(), "db.sqlite3"))

database_path = relative_path_backend()
DATABASE_URL = f"sqlite:///{database_path}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def create_database():
    """Creates all tables in the database engine."""
    Base.metadata.create_all(engine)

create_database()