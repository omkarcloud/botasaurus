from hashlib import sha256
import json
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime, timezone
from .cleaners import normalize_dicts_by_fieldnames

Base = declarative_base()


class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


def calculate_duration(obj):
    end_time = obj.finished_at if obj.finished_at else datetime.now(timezone.utc).replace(tzinfo=None)
    if obj.started_at:
        duration = (end_time - obj.started_at).total_seconds()

        if duration == 0:
          return 0

        result = float(format(duration, '.2f'))
        
        return result

    return None


def isoformat(obj):
    return obj.isoformat() if obj else None


def serialize_task(obj, with_result):
    if with_result:
        result = {"result": obj.result}
    else:
        result = {}

    task_id = obj.id
    return {
        "id": task_id,
        "status": obj.status,
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
    result = Column(JSON)  # JSON field for storing result data
    result_count = Column(Integer, default=0)  # Integer field for storing result count, default 0

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def to_json(self):
        """Serializes all properties of the Task object into a JSON dictionary."""
        return serialize_task(self, with_result=True)


class Cache(Base):
    __tablename__ = "caches"

    id = Column(Integer, primary_key=True)
    key = Column(String, index=True, unique=True)
    result = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def to_json(self):
        return {
            "id": self.id,
            "key": self.key,
            "result": self.result,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


def create_cache_key(scraper_type, data):
    return scraper_type + '-' + sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def check_cache_exists(session, key):
    return session.query(Cache).filter(Cache.key == key).count() > 0

def create_cache(session, scraper_type, data, result):
    key = create_cache_key(scraper_type, data)
    
    if check_cache_exists(session, key):
        session.query(Cache).filter(Cache.key == key).update({"result": result})
    else: 
        cache = Cache(key=key, result=result)
        session.add(cache)


class TaskHelper:
    @staticmethod
    def get_completed_children_results(session, parent_id, except_task_id=None):
        query = session.query(Task).filter(
            Task.parent_task_id == parent_id, Task.status == TaskStatus.COMPLETED
        )
        if except_task_id:
            query = query.filter(Task.id != except_task_id)
        query = query.all()

        all_results = []
        for child in query:
            all_results.extend(child.result)
        return normalize_dicts_by_fieldnames(all_results)

    @staticmethod
    def is_parents_last_task(session, parent_id, except_task_id=None):
        done_children_count = TaskHelper.get_done_children_count(
            session, parent_id, except_task_id
        )
        child_count = TaskHelper.get_all_children_count(
            session, parent_id, except_task_id
        )

        return done_children_count == child_count

    @staticmethod
    def get_all_children_count(session, parent_id, except_task_id=None):
        query = session.query(Task).filter(Task.parent_task_id == parent_id)
        if except_task_id:
            query = query.filter(Task.id != except_task_id)

        return query.count()

    @staticmethod
    def get_done_children_count(session, parent_id, except_task_id=None):
        query = session.query(Task).filter(
            Task.parent_task_id == parent_id,
            Task.status.in_(
                [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.ABORTED]
            ),
        )
        if except_task_id:
            query = query.filter(Task.id != except_task_id)

        return query.count()

    @staticmethod
    def is_task_completed_or_failed(session, task_id):
        return (
            session.query(Task)
            .filter(
                Task.id == task_id,
                Task.status.in_(
                    [
                        TaskStatus.COMPLETED,
                        TaskStatus.FAILED,
                    ]
                ),
            )
            .count()
            != 0
        )

    @staticmethod
    def get_pending_or_executing_child_count(session, parent_id, except_task_id=None):
        query = session.query(Task).filter(
            Task.parent_task_id == parent_id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
        )
        if except_task_id:
            query = query.filter(Task.id != except_task_id)

        return query.count()

    @staticmethod
    def get_failed_children_count(session, parent_id, except_task_id=None):
        query = session.query(Task).filter(
            Task.parent_task_id == parent_id, Task.status == TaskStatus.FAILED
        )
        if except_task_id:
            query = query.filter(Task.id != except_task_id)

        return query.count()

    @staticmethod
    def get_aborted_children_count(session, parent_id, except_task_id=None):
        query = session.query(Task).filter(
            Task.parent_task_id == parent_id, Task.status == TaskStatus.ABORTED
        )
        if except_task_id:
            query = query.filter(Task.id != except_task_id)

        return query.count()

    @staticmethod
    def delete_task(session, task_id):
        return session.query(Task).filter(Task.id == task_id).delete()

    @staticmethod
    def delete_child_tasks(session, task_id):
        return session.query(Task).filter(Task.parent_task_id == task_id).delete()

    @staticmethod
    def update_task(session, task_id, data, in_status=None):
        query = session.query(Task).filter(Task.id == task_id)
        if in_status:
            query = query.filter(Task.status.in_(in_status))

        return query.update(data)

    @staticmethod
    def fail_task(session, task_id):
        return TaskHelper.update_task(
            session,
            task_id,
            {
                "result": None,
                "status": TaskStatus.FAILED,
                "finished_at": datetime.now(timezone.utc),
            },
        )

    @staticmethod
    def abort_task(session, task_id):
        session.query(Task).filter(
            Task.id == task_id,
            Task.finished_at.is_(None),
        ).update({"finished_at": datetime.now(timezone.utc)})

        return TaskHelper.update_task(
            session,
            task_id,
            {"status": TaskStatus.ABORTED, },
        )

    @staticmethod
    def abort_child_tasks(session, task_id):
        session.query(Task).filter(
            Task.parent_task_id == task_id,
            Task.finished_at.is_(None),
        ).update({"finished_at": datetime.now(timezone.utc)})

        return (
            session.query(Task)
            .filter(Task.parent_task_id == task_id)
            .update({"status": TaskStatus.ABORTED,})
        )

    @staticmethod
    def success_all_task(session, parent_id, except_task_id=None):
        all_results = TaskHelper.get_completed_children_results(
            session, parent_id, except_task_id
        )
        
        return TaskHelper.update_task(
            session,
            parent_id,
            {
                "result": all_results,
                "result_count": len(all_results),
                "status": TaskStatus.COMPLETED,
                "finished_at": datetime.now(timezone.utc),
            },
        )

    @staticmethod
    def update_parent_task_results(session, parent_id, except_task_id=None):
        all_results = TaskHelper.get_completed_children_results(
            session, parent_id, except_task_id
        )
        
        return TaskHelper.update_task(
            session,
            parent_id,
            {
                "result": all_results,
                "result_count": len(all_results),
            },
        )    

    @staticmethod
    def get_task(session, task_id, in_status=None):
        if in_status:
            return (
                session.query(Task)
                .filter(Task.id == task_id, Task.status.in_(in_status))
                .first()
            )
        else:
            return session.get(Task, task_id)

    @staticmethod
    def get_tasks_by_ids(session, task_ids):
        return session.query(Task).filter(Task.id.in_(task_ids)).all()