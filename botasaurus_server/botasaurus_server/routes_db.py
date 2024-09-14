from .models import (
    Task,
    TaskStatus,
    serialize_task,
    serialize_ui_display_task,
    serialize_ui_output_task,
)
from .task_helper import TaskHelper
from .db_setup import Session
from .task_results import TaskResults, create_cache_key
from .retry_on_db_error import retry_on_db_error

@retry_on_db_error
def perform_create_all_task(
    data, metadata, is_sync, scraper_name, scraper_type, all_task_sort_id
):
    with Session() as session:
        all_task = Task(
            status=TaskStatus.PENDING,
            scraper_name=scraper_name,
            scraper_type=scraper_type,
            is_all_task=True,
            is_sync=is_sync,
            parent_task_id=None,
            data=data,
            meta_data=metadata,
            task_name="All Task",
            sort_id=all_task_sort_id,  # Set the sort_id for the all task
        )
        session.add(all_task)
        session.commit()

        all_task_id = all_task.id
        return serialize(all_task), all_task_id

@retry_on_db_error
def perform_create_tasks(tasks, cached_tasks=None):
    with Session() as session:
        session.add_all(tasks)
        session.commit()

        if cached_tasks:
            file_list = [
                (
                    t.id,
                    t.result,
                )
                for t in cached_tasks
            ]
            parallel_create_files(file_list)

        # basically here we will write cache, as each cached task adds a property called __cached__result = None [default]
        # but it set when going over cache
        return serialize(tasks)

@retry_on_db_error
def perform_complete_task(all_task_id, remove_duplicates_by):
    executor.complete_as_much_all_task_as_possible(all_task_id, remove_duplicates_by)

@retry_on_db_error
def is_task_done(task_id):
    with Session() as session:
        x = TaskHelper.is_task_completed_or_failed(session, task_id)
    return x

@retry_on_db_error
def queryTasks(ets, with_results, page=None, per_page=None, serializer=serialize_task):
    with Session() as session:

        tasks_query = session.query(Task).with_entities(*ets)
        total_count = tasks_query.count()

        if per_page is None:
            per_page = 1 if total_count == 0 else total_count
            page = 1
        else:
            per_page = int(per_page)

        total_pages = max((total_count + per_page - 1) // per_page, 1)

        page = int(page)
        page = max(min(page, total_pages), 1)  # Ensure page is within valid range

        # Apply pagination if page and per_page are provided and valid
        tasks_query = tasks_query.order_by(Task.sort_id.desc())
        if per_page is not None:
            per_page = int(per_page)
            start = (page - 1) * per_page
            tasks_query = tasks_query.limit(per_page).offset(start)

        tasks = tasks_query.all()

        current_page = page if page is not None else 1
        next_page = (
            current_page + 1 if (current_page * per_page) < total_count else None
        )
        previous_page = current_page - 1 if current_page > 1 else None

        if next_page:
            next_page = create_page_url(next_page, per_page, with_results)

        if previous_page:
            previous_page = create_page_url(previous_page, per_page, with_results)

        return jsonify(
            {
                "count": total_count,
                "total_pages": total_pages,
                "next": next_page,
                "previous": previous_page,
                "results": [serializer(task, with_results) for task in tasks],
            }
        )

@retry_on_db_error
def get_task_from_db(task_id):
    with Session() as session:
        task = TaskHelper.get_task(session, task_id)
        if task:
            return serialize(task)
        else:
            raise create_task_not_found_error(task_id)

@retry_on_db_error
def perform_is_any_task_finished(pending_task_ids, progress_task_ids, all_tasks):
    with Session() as session:
        all_tasks_query = [
            and_(Task.id == x["id"], Task.result_count > x["result_count"])
            for x in all_tasks
        ]
        is_any_task_finished = (
            session.query(Task.id)
            .filter(
                or_(
                    and_(
                        Task.id.in_(pending_task_ids), Task.status != TaskStatus.PENDING
                    ),
                    and_(
                        Task.id.in_(progress_task_ids),
                        Task.status != TaskStatus.IN_PROGRESS,
                    ),
                    *all_tasks_query,
                )
            )
            .first()
            is not None
        )

    return is_any_task_finished

@retry_on_db_error
def perform_is_task_updated(task_id):
    with Session() as session:
        task_data = (
            session.query(Task.updated_at, Task.status)
            .filter(Task.id == task_id)
            .first()
        )
    return task_data

@retry_on_db_error
def perform_get_task_results(task_id):
    with Session() as session:
        task = TaskHelper.get_task_with_entities(
            session,
            task_id,
            [Task.scraper_name, Task.result_count, Task.is_all_task, Task.data],
        )
        if not task:
            raise create_task_not_found_error(task_id)

        scraper_name = task.scraper_name
        task_data = task.data
        is_all_task = task.is_all_task
        result_count = task.result_count
    return scraper_name, is_all_task, task_data, result_count

@retry_on_db_error
def perform_download_task_results(task_id):
    with Session() as session:
        task = TaskHelper.get_task_with_entities(
            session,
            task_id,
            [
                Task.scraper_name,
                Task.is_all_task,
                Task.data,
                Task.is_all_task,
                Task.task_name,
            ],
        )
        if not task:
            raise create_task_not_found_error(task_id)

        scraper_name = task.scraper_name
        task_data = task.data
        is_all_task = task.is_all_task
        task_name = task.task_name
        is_all_task = task.is_all_task

    return (
        scraper_name,
        (
            TaskResults.get_all_task(task_id)
            if is_all_task
            else TaskResults.get_task(task_id)
        ),
        task_data,
        is_all_task,
        task_name,
    )

@retry_on_db_error
def perform_get_ui_task_results(task_id):
    with Session() as session:
        task = TaskHelper.get_task_with_entities(
            session,
            task_id,
            [
                Task.scraper_name,
                Task.result_count,
                Task.is_all_task,
                Task.data,
                Task.updated_at,
                Task.status,
            ],
        )
        if not task:
            raise create_task_not_found_error(task_id)

        scraper_name = task.scraper_name
        task_data = task.data
        is_all_task = task.is_all_task
        result_count = task.result_count
        serialized_task = serialize_ui_display_task(task)

    return scraper_name, is_all_task, serialized_task, task_data, result_count

@retry_on_db_error
def perform_patch_task(action, task_id):

    with Session() as session:
        task = (
            session.query(
                Task.id,
                Task.is_all_task,
                Task.parent_task_id,
                Task.scraper_name,
            )
            .filter(Task.id == task_id)
            .first()
        )
    if task:
        remove_duplicates_by = Server.get_remove_duplicates_by(task[-1])
        task = task[0:3]
        if action == "delete":
            delete_task(*task, remove_duplicates_by)
        elif action == "abort":
            abort_task(*task, remove_duplicates_by)

