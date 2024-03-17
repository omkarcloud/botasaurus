from datetime import datetime, timezone
from threading import Thread, Lock
import time
from math import inf
from sqlalchemy import and_
import traceback
from sqlalchemy.exc import OperationalError
from .cleaners import clean_data
from .db_setup import Session
from .server import Server
from .models import Task, TaskStatus, TaskHelper, create_cache
from .scraper_type import ScraperType

class TaskExecutor:

    def load(self):
        self.current_capacity = {"browser": 0, "request": 0}
        self.lock = Lock()

    def start(self):
        with Session() as session:
            # Delete tasks with is_sync=True and status as either pending or in progress
            session.query(Task).filter(
                and_(
                    Task.is_sync == True,
                    Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                )
            ).delete()
            # Update in progress tasks to pending
            session.query(Task).filter(Task.status == TaskStatus.IN_PROGRESS).update(
                {"status": TaskStatus.PENDING, "started_at": None},
            )
            session.commit()
        Thread(target=self.task_worker, daemon=True).start()

    def task_worker(self):
        while True:
            with Session() as session:
                try:
                    if Server.get_browser_scrapers():
                        self.process_tasks(session, ScraperType.BROWSER)
                        session.commit()

                    if Server.get_request_scrapers():
                        self.process_tasks(session, ScraperType.REQUEST)
                        session.commit()

                except OperationalError as e:
                    session.rollback()  # Roll back in case of errors
                    print(f"An OperationalError occurred: {e}")  # Log the error

            time.sleep(0.1)

    def process_tasks(self, session, scraper_type):
        rate_limit = self.get_max_running_count(scraper_type)
        current_count = self.get_current_running_count(scraper_type)

        self.execute_pending_tasks(
            session,
            and_(
                Task.status == TaskStatus.PENDING,
                Task.scraper_type == scraper_type,
                Task.is_all_task == False,
            ),
            current_count,
            rate_limit,
            scraper_type
        )

    def get_max_running_count(self, scraper_type):
        return Server.get_rate_limit()[scraper_type]

    def get_current_running_count(self, scraper_type):
        return self.current_capacity[scraper_type]

    def execute_pending_tasks(self, session, task_filter, current, limit, scraper_type):
        if current < limit:
            query = (
                session.query(Task).filter(task_filter).order_by(Task.is_sync.desc()) # Prioritize syncronous tasks
            )
            if limit != inf:
                remaining = limit - current
                query = query.limit(remaining)

            tasks = query.all()

            # Collect task and parent IDs
            task_ids = [task.id for task in tasks]
            parent_ids = {task.parent_task_id for task in tasks if task.parent_task_id}

            # Bulk update the status of tasks
            if task_ids:
                session.query(Task).filter(Task.id.in_(task_ids)).update(
                    {"status": TaskStatus.IN_PROGRESS, "started_at": datetime.now(timezone.utc)}
                )

            # Bulk update the status of parent tasks
            if parent_ids:
                session.query(Task).filter(
                    Task.id.in_(list(parent_ids)), Task.started_at.is_(None)
                ).update(
                    {"status": TaskStatus.IN_PROGRESS, "started_at": datetime.now(timezone.utc)}
                )

            # Commit the changes
            session.commit()

            # Start tasks after commit
            for task in tasks:
                self.run_task_and_update_state(scraper_type, task.to_json())

    def run_task_and_update_state(self, scraper_type, task_json):
        Thread(
                target=self.run_task, args=(task_json,), daemon=True
                ).start()
        
        self.increment_capacity(scraper_type)

    def increment_capacity(self, scraper_type):
        with self.lock:
            self.current_capacity[scraper_type] += 1

    def decrement_capcity(self, scraper_type):
        with self.lock:
            self.current_capacity[scraper_type] -= 1

    def run_task(self, task):

        scraper_type = task["scraper_type"]
        task_id = task["id"]
        scraper_name = task["scraper_name"]
        metadata = {"metadata": task["metadata"]} if task["metadata"] != {} else {}
        task_data = task["data"]

        fn = Server.get_scraping_function(scraper_name)

        try:
            result = fn(
                task_data,
                **metadata,
                parallel=None,
                cache=False,
                beep=False,
                run_async=False,
                async_queue=False,
                raise_exception=True,
                close_on_crash=True,
                output=None,
                create_error_logs=False
            )

            result = clean_data(result)

            self.mark_task_as_success(task_id, result)

        except Exception:
            exception_log = traceback.format_exc()
            traceback.print_exc()
            self.mark_task_as_failure(task_id, exception_log)
        finally:
            self.decrement_capcity(scraper_type)
            self.update_parent_task(task_id)

    def update_parent_task(self, task_id):
        with Session() as session:
            task_to_update = session.get(Task, task_id)
            parent_id = task_to_update.parent_task_id
            if task_to_update and parent_id:
                self.complete_parent_task_if_possible(session, parent_id)

    def complete_parent_task_if_possible(self, session,  parent_id):
                    # ensures it is in valid pending state
            parent_task = TaskHelper.get_task(
                        session,
                        parent_id,
                        [TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
                    )

            if parent_task:
                is_last_task = TaskHelper.is_parents_last_task(
                            session, parent_id
                        )
                if is_last_task:
                    failed_children_count = (
                                TaskHelper.get_failed_children_count(session, parent_id)
                            )
                    if failed_children_count:
                        TaskHelper.fail_task(
                                    session,
                                    parent_id,
                                )
                    else:
                        TaskHelper.success_all_task(session, parent_id)

                    session.commit()
                else: 
                    TaskHelper.update_parent_task_results(
                                        session,
                                        parent_id,
                                    )
                    session.commit()


    def mark_task_as_failure(self, task_id, exception_log):
        with Session() as session:
            TaskHelper.update_task(
                    session,
                    task_id,
                    {
                        "result": exception_log,
                        "status": TaskStatus.FAILED,
                        "finished_at": datetime.now(timezone.utc),
                    },
                    [TaskStatus.IN_PROGRESS],
                )
            session.commit()

    def mark_task_as_success(self, task_id, result):
        with Session() as session:
            TaskHelper.update_task(
                    session,
                    task_id,
                    {
                        "result": result,
                        "result_count": len(result),
                        "status": TaskStatus.COMPLETED,
                        "finished_at": datetime.now(timezone.utc),
                    },
                    [TaskStatus.IN_PROGRESS],
                )
            
            if Server.cache:
                task = TaskHelper.get_task(session, task_id)
                scraper_name = task.scraper_name
                data = task.data
                create_cache(session,scraper_name  , data, result)
            
            session.commit()
