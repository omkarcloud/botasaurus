import subprocess
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import path, getcwd
from os import makedirs
from shutil import rmtree
from .env import is_master
from .models import Base  # Assuming Task is one of your models
from .server import Server  # Assuming Task is one of your models
from .utils import path_task_results, path_task_results_tasks, path_task_results_cache

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def dynamically_import_postgres():
    try:
        import psycopg2
    except ImportError:
        install('psycopg2-binary')

def relative_path_backend():
        """Determines the relative path to the database file, prioritizing 'backend/db.sqlite3'."""
        if is_master:
            return path.abspath(path.join(getcwd(), "..", "db", "db.sqlite3"))
        else:
            return path.abspath(path.join(getcwd(), "db.sqlite3"))

database_path = relative_path_backend()
def get_sqlite_url():
    return f"sqlite:///{database_path}" 


def clean_database_url(url):
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        dynamically_import_postgres()
    return url

# TODO: for now commented, later if needed add back
# if not path.exists(database_path):
#     rmtree(relative_path_task_results(), ignore_errors=True)

def ensure_directory_exists(x):
    if not path.exists(x):
        makedirs(x)

ensure_directory_exists(path_task_results)
ensure_directory_exists(path_task_results_tasks)
ensure_directory_exists(path_task_results_cache)

db_url = clean_database_url(Server.database_url) if Server.database_url else get_sqlite_url()
Server._is_database_initialized = True
engine = create_engine(db_url, **(Server.database_options or {}))
Session = sessionmaker(bind=engine)

def create_database():
    """Creates all tables in the database engine."""
    Base.metadata.create_all(engine)

create_database()