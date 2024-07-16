from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from datetime import datetime, timezone

from .task_results import TaskResults

Base = declarative_base()


class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"

def remove_duplicates_by_key(dict_list, key):
    """
    Removes duplicates from a list of dictionaries based on a specified key.
    
    :param dict_list: List of dictionaries from which duplicates will be removed.
    :param key: The key based on which duplicates are identified and removed.
    :return: A list of dictionaries with duplicates removed.
    """
    seen = set()
    new_dict_list = []
    for d in dict_list:
        if key in d:
            if d[key] not in seen:
                seen.add(d[key])
                new_dict_list.append(d)
        else: 
            new_dict_list.append(d)
    return new_dict_list

def calculate_duration(obj):
    if obj.started_at:
        end_time = (
            obj.finished_at
            if obj.finished_at
            else datetime.now(timezone.utc).replace(tzinfo=None)
        )
        duration = (end_time - obj.started_at).total_seconds()

        if duration == 0:
            return 0

        result = float(format(duration, ".2f"))

        return result

    return None


def isoformat(obj):
    return obj.isoformat() if obj else None


def serialize_ui_output_task(obj, _):
    task_id = obj.id

    return {
        "id": task_id,
        "status": obj.status,
        "task_name": obj.task_name if obj.task_name is not None else f"Task {task_id}",
        "result_count": obj.result_count,
        "is_all_task": obj.is_all_task,
        "started_at": isoformat(obj.started_at),
        "finished_at": isoformat(obj.finished_at),
    }


def serialize_ui_display_task(obj):
    return {
        "scraper_name": obj.scraper_name,
        "status": obj.status,
        "updated_at": isoformat(obj.updated_at),
    }


def serialize_task(obj, with_result):
    task_id = obj.id
    status = obj.status    
    if with_result:
        if status == TaskStatus.PENDING:
            result = {"result": None}
        elif status != TaskStatus.IN_PROGRESS or obj.is_all_task:
            # set in cache
            if not hasattr(obj, "result"):
                result = {"result":  TaskResults.get_all_task(task_id) if obj.is_all_task else TaskResults.get_task(task_id)}
            else:
                result = {"result": obj.result}
        else:
            result = {"result": None}
    else:
        result = {}
    return {
        "id": task_id,
        "status": status,
        "task_name": obj.task_name if obj.task_name is not None else f"Task {task_id}",
        "scraper_name": obj.scraper_name,
        "scraper_type": obj.scraper_type,
        "is_all_task": obj.is_all_task,
        "is_sync": obj.is_sync,
        "parent_task_id": obj.parent_task_id,
        "duration": calculate_duration(obj),
        "started_at": isoformat(obj.started_at),
        "finished_at": isoformat(obj.finished_at),
        "data": obj.data,
        "metadata": obj.meta_data,
        **result,
        "result_count": obj.result_count,
        "created_at": isoformat(obj.created_at),
        "updated_at": isoformat(obj.updated_at),
    }


class Task(Base):
    __tablename__ = "tasks"

    # Identifiers and status
    id = Column(Integer, primary_key=True)
    status = Column(String, index=True)

    sort_id = Column(Integer, index=True)  # Private sort id

    # Task details
    task_name = Column(String, index=True)
    scraper_name = Column(String, index=True)
    scraper_type = Column(String, index=True)
    is_all_task = Column(Boolean, index=True)
    is_sync = Column(Boolean, index=True)  # Indexed column with default value False

    # Parent task relationship (optional)
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    # Data fields
    data = Column(JSON)  # JSON field for storing task data
    meta_data = Column(JSON)  # JSON field for storing meta data
    result_count = Column(
        Integer, default=0
    )  # Integer field for storing result count, default 0

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_json(self):
        """Serializes all properties of the Task object into a JSON dictionary."""
        return serialize_task(self, with_result=True)
