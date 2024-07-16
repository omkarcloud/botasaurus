from datetime import datetime, timezone
from sqlalchemy import update
from botasaurus_server.db_setup import Session
from .cleaners import normalize_dicts_by_fieldnames
from .task_results import TaskResults
from botasaurus import bt

from .models import Task, TaskStatus, remove_duplicates_by_key
from .db_setup import Session

class TaskHelper:
    @staticmethod
    def get_completed_children_results(parent_id, except_task_id, remove_duplicates_by):
        with Session() as session:
            query = session.query(Task.id).filter(
                Task.parent_task_id == parent_id, Task.status == TaskStatus.COMPLETED
            )
            if except_task_id:
                query = query.filter(Task.id != except_task_id)
            query = query.all()
            query = [q[0] for q in query]
        
        all_results = bt.flatten(TaskResults.get_tasks(query))
        rs = normalize_dicts_by_fieldnames(all_results)
        
        if remove_duplicates_by:
           rs = remove_duplicates_by_key(rs, remove_duplicates_by)
        return rs

    @staticmethod
    def are_all_child_task_done(session, parent_id):
        done_children_count = TaskHelper.get_done_children_count(
            session, parent_id, 
        )
        child_count = TaskHelper.get_all_children_count(
            session, parent_id,
        )

        return done_children_count == child_count

    @staticmethod
    def get_all_children_count(session, parent_id, except_task_id=None):
        query = session.query(Task.id).filter(Task.parent_task_id == parent_id)
        if except_task_id:
            query = query.filter(Task.id != except_task_id)

        return query.count()

    @staticmethod
    def get_done_children_count(session, parent_id, except_task_id=None):
        query = session.query(Task.id).filter(
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
            session.query(Task.id)
            .filter(
                Task.id == task_id,
                Task.status.in_(
                    [
                        TaskStatus.COMPLETED,
                        TaskStatus.FAILED,
                    ]
                ),
            )
            .first()
            is not None
        )

    @staticmethod
    def get_pending_or_executing_child_count(session, parent_id, except_task_id=None):
        query = session.query(Task.id).filter(
            Task.parent_task_id == parent_id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
        )
        if except_task_id:
            query = query.filter(Task.id != except_task_id)

        return query.count()

    @staticmethod
    def get_failed_children_count(session, parent_id, except_task_id=None):
        query = session.query(Task.id).filter(
            Task.parent_task_id == parent_id, Task.status == TaskStatus.FAILED
        )
        if except_task_id:
            query = query.filter(Task.id != except_task_id)

        return query.count()

    @staticmethod
    def get_aborted_children_count(session, parent_id, except_task_id=None):
        query = session.query(Task.id).filter(
            Task.parent_task_id == parent_id, Task.status == TaskStatus.ABORTED
        )
        if except_task_id:
            query = query.filter(Task.id != except_task_id)

        return query.count()

    @staticmethod
    def delete_task(session, task_id, is_all_task):
        session.query(Task).filter(Task.id == task_id).delete()
        if is_all_task:
            TaskResults.delete_all_task(task_id)
        else:
            TaskResults.delete_task(task_id)


    @staticmethod
    def delete_child_tasks(session, task_id):
        query = session.query(Task.id).filter(Task.parent_task_id == task_id)
        ids = [q[0] for q in query.all()]
        
        session.query(Task).filter(Task.parent_task_id == task_id).delete()
        TaskResults.delete_tasks(ids)

    @staticmethod
    def update_task(session, task_id, data, in_status=None):
        query = session.query(Task).filter(Task.id == task_id)
        if in_status:
            query = query.filter(Task.status.in_(in_status))

        return query.update(data)


    @staticmethod
    def abort_task(session, task_id):
        session.query(Task).filter(
            Task.id == task_id,
            Task.finished_at.is_(None),
        ).update({"finished_at": datetime.now(timezone.utc)})

        return TaskHelper.update_task(
            session,
            task_id,
            {
                "status": TaskStatus.ABORTED,
            },
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
            .update(
                {
                    "status": TaskStatus.ABORTED,
                }
            )
        )

    @staticmethod
    def collect_and_save_all_task(parent_id, except_task_id, remove_duplicates_by, status):
        all_results = TaskHelper.get_completed_children_results(
            parent_id, except_task_id, remove_duplicates_by
        )
        TaskResults.save_all_task(parent_id, all_results)
        
        with Session() as session:
            TaskHelper.update_task(
                session,
                parent_id,
                {
                    "result_count": len(all_results),
                    "status": status,
                    "finished_at": datetime.now(timezone.utc),
                },
            )
            session.commit()

    @staticmethod
    def read_clean_save_task(parent_id,  remove_duplicates_by, status):
        
        rs = normalize_dicts_by_fieldnames(TaskResults.get_all_task(parent_id))
        
        if remove_duplicates_by:
           rs = remove_duplicates_by_key(rs, remove_duplicates_by)
        TaskResults.save_all_task(parent_id, rs)
        
        with Session() as session:
            TaskHelper.update_task(
                session,
                parent_id,
                {
                    "result_count": len(rs),  # Fixed to correctly update with rs length after removing duplicates
                    "status": status,
                    "finished_at": datetime.now(timezone.utc),
                },
            )
            session.commit()

    @staticmethod
    def update_parent_task_results(parent_id, result):
        if result:
            TaskResults.append_all_task(parent_id, result)

            with Session() as session:
                session.execute(
                    update(Task).where(Task.id == parent_id).values(result_count=Task.result_count + len(result))
                )
                session.commit()

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
    def get_task_with_entities(session, task_id, entities):
        return (
            session.query(Task)
            .with_entities(*entities)
            .filter(Task.id == task_id)
            .first()
        )

    @staticmethod
    def get_tasks_by_ids(session, task_ids):
        return session.query(Task).filter(Task.id.in_(task_ids)).all()