from datetime import datetime, timezone
from threading import Thread, Lock
import time
from math import inf
from sqlalchemy import and_
import traceback
from .cleaners import clean_data
from .db_setup import Session
from .server import Server
from .models import Task, TaskStatus, remove_duplicates_by_key
from .task_helper import TaskHelper
from .scraper_type import ScraperType
from .retry_on_db_error import retry_on_db_error
from .task_results import TaskResults
from botasaurus.dontcache import is_dont_cache

class TaskExecutor:

    def load(self):
        self.current_capacity = {"browser": 0, "request": 0, "task": 0}
        self.lock = Lock()
    
    def start(self):
        self.fix_in_progress_tasks()
        Thread(target=self.task_worker, daemon=True).start()
    
    @retry_on_db_error
    def fix_in_progress_tasks(self):
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


    def task_worker(self):
        browser_scrapers = len(Server.get_browser_scrapers()) > 0
        request_scrapers = len(Server.get_request_scrapers()) > 0
        task_scrapers = len(Server.get_task_scrapers()) > 0
        
        while True:
            try:
                if browser_scrapers:
                    self.process_tasks(ScraperType.BROWSER)

                if request_scrapers:
                    self.process_tasks(ScraperType.REQUEST)

                if task_scrapers:
                    self.process_tasks(ScraperType.TASK)
            except:
              traceback.print_exc()

            time.sleep(1)

    def process_tasks(self, scraper_type):
        rate_limit = self.get_max_running_count(scraper_type)
        current_count = self.get_current_running_count(scraper_type)
        if current_count < rate_limit:
            self.execute_pending_tasks(
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

    @retry_on_db_error
    def execute_pending_tasks(self, task_filter, current, limit, scraper_type):
            with Session() as session:
                query = (
                    session.query(Task).filter(task_filter).order_by(Task.sort_id.desc(), Task.is_sync.desc()) # Prioritize syncronous tasks
                )
                if limit != inf:
                    remaining = limit - current
                    query = query.limit(remaining)

                tasks = query.all()

                if tasks:
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

                    session.commit()

                    # Start tasks after commit
                    for task in tasks:
                        self.run_task_and_update_state(scraper_type, task.to_json())

    def run_task_and_update_state(self, scraper_type, task_json):
        Thread(target=self.run_task, args=(task_json,), daemon=True).start()
        self.increment_capacity(scraper_type)
        

    def increment_capacity(self, scraper_type):
        # Temp Lock Disabling to check if it reduces the deadlock on vm tasks
        # with self.lock:
            self.current_capacity[scraper_type] += 1

    def decrement_capcity(self, scraper_type):
        # Temp Lock Disabling to check if it reduces the deadlock on vm tasks
        # with self.lock:
            self.current_capacity[scraper_type] -= 1

    def run_task(self, task):

        scraper_type = task["scraper_type"]
        task_id = task["id"]
        scraper_name = task["scraper_name"]
        parent_task_id = task["parent_task_id"]
        metadata = {"metadata": task["metadata"]} if task["metadata"] != {} else {}
        task_data = task["data"]

        fn = Server.get_scraping_function(scraper_name)
        exception_log = None
        try:
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
                    create_error_logs=False,
                    return_dont_cache_as_is=True
                )
                if is_dont_cache(result):
                    is_result_dont_cached = True
                    # unpack
                    result = result.data
                else: 
                    is_result_dont_cached = False

                result = clean_data(result)

                remove_duplicates_by = Server.get_remove_duplicates_by(scraper_name)
                if remove_duplicates_by:
                   result = remove_duplicates_by_key(result, remove_duplicates_by)

                if is_result_dont_cached:
                    self.mark_task_as_success(task_id, result, False, scraper_name, task_data)
                else:
                    self.mark_task_as_success(task_id, result, Server.cache, scraper_name, task_data)
                self.decrement_capcity(scraper_type)
            except:
                self.decrement_capcity(scraper_type)
                exception_log = traceback.format_exc()
                traceback.print_exc()
                self.mark_task_as_failure(task_id, exception_log)
            finally:
                if parent_task_id:
                    if exception_log:
                        self.update_parent_task(task_id, [])
                    else:
                        self.update_parent_task(task_id, result)
        except Exception as e:
          traceback.print_exc()
          print("Error in run_task ", e)
    
    @retry_on_db_error
    def update_parent_task(self, task_id, result):
        with Session() as session:
            task_to_update = session.get(Task, task_id)
            parent_id = task_to_update.parent_task_id
            scraper_name = task_to_update.scraper_name
        
        if parent_id:
            self.complete_parent_task_if_possible(parent_id, Server.get_remove_duplicates_by(scraper_name), result)

    def complete_parent_task_if_possible(self,parent_id, remove_duplicates_by, result):
            fn = None
            with Session() as session:
                parent_task = TaskHelper.get_task(
                            session,
                            parent_id,
                            [TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
                        )

                # MAY BE DELETED SO CHECK
                if parent_task:
                    # is fast no worry
                    TaskHelper.update_parent_task_results(parent_id,result,)
                    is_done = TaskHelper.are_all_child_task_done(
                                session, parent_id
                            )
                    if is_done:
                        failed_children_count = TaskHelper.get_failed_children_count(session, parent_id)
                        
                        status = TaskStatus.FAILED if failed_children_count else TaskStatus.COMPLETED
                        fn = lambda: TaskHelper.read_clean_save_task(parent_id, remove_duplicates_by, status)
                        
            if fn:
                fn()          

    def complete_as_much_all_task_as_possible(self,parent_id, remove_duplicates_by):
            fn = None
            with Session() as session:
                    is_done = TaskHelper.are_all_child_task_done(
                                session, parent_id
                            )
                    if is_done:
                        failed_children_count = TaskHelper.get_failed_children_count(session, parent_id)
                        status = TaskStatus.FAILED if failed_children_count else TaskStatus.COMPLETED
                        fn = lambda: TaskHelper.collect_and_save_all_task(parent_id, None, remove_duplicates_by, status)
                    else:
                        fn = lambda: TaskHelper.collect_and_save_all_task(parent_id, None, remove_duplicates_by, TaskStatus.IN_PROGRESS)
            if fn:
                fn()  

    @retry_on_db_error
    def mark_task_as_failure(self, task_id, exception_log):
        TaskResults.save_task(task_id, exception_log)
        with Session() as session:
            TaskHelper.update_task(
                    session,
                    task_id,
                    {
                        "status": TaskStatus.FAILED,
                        "finished_at": datetime.now(timezone.utc),
                    },
                    [TaskStatus.IN_PROGRESS],
                )
            session.commit()
    
    @retry_on_db_error
    def mark_task_as_success(self, task_id, result, cache_task, scraper_name, data):
        TaskResults.save_task(task_id, result)
        if cache_task:
            TaskResults.save_cached_task(scraper_name, data, result)
        with Session() as session:

            update_result = TaskHelper.update_task(
                    session,
                    task_id,
                    {
                        "result_count": len(result),
                        "status": TaskStatus.COMPLETED,
                        "finished_at": datetime.now(timezone.utc),
                    },
                    [TaskStatus.IN_PROGRESS],
                )
            if not update_result:
                # if the task is aborted in progress, there should be no results
                TaskResults.delete_task(task_id)

            session.commit()
