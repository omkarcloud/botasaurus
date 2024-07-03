from casefy import titlecase
import os
from math import inf
from hashlib import sha256
from .sorts import Sort
from .scraper_type import ScraperType
from .controls_adapter import ControlsAdapter

def relative_path(path, goback=0):
    levels = [".."] * (goback + -1)
    return os.path.abspath(os.path.join(os.getcwd(), *levels, path.strip()))

def compute_hash(content):
    return sha256(content.encode("utf-8")).hexdigest()


def get_readme():
    try:
        with open("README.md", encoding="utf-8") as readme_file:
            text = readme_file.read()
        return text
    except FileNotFoundError:
        return ""


class _Server:
    def __init__(self):
        self.scrapers = {}
        self.rate_limit = {"browser": 1, "request": 30, "task": 30}
        self.controls_cache = {}  # Cache to store Controls instances
        self.cache = False
        self.config = None
        self.database_url = None
        self.database_options = None
        self._is_database_initialized = False

    def set_database_url(self, database_url=None, database_options=None):
        if self._is_database_initialized:
            raise Exception('The database has already been initialized. To resolve this error, ensure that the line ("from botasaurus_server.run import run") comes after the line ("import backend.scrapers") in the "run.py" file.')
        self.database_url = database_url
        self.database_options = database_options


    def get_config(self):
        if not self.config:
            self.config = {
                "title": "Botasaurus",
                "header_title": "Botasaurus",
                "description": "Build Awesome Scrapers with Botasaurus, The All in One Scraping Framework.",
                "right_header": {
                    "text": "Love It? Star It! ★",
                    "link": "https://github.com/omkarcloud/botasaurus",
                },
                "readme": get_readme(),
            }
        return self.config

    def configure(
        self,
        title="",
        header_title="",
        description="",
        right_header={"text": "", "link": ""},
        readme="",
    ):
        """
        Creates a configuration dictionary for scraper.

        :param header_title (str, optional): The title to be displayed in the header section of the page.
        :param description (str, optional): A brief description of the Scraper.
        :param right_header (dict, optional): A dictionary containing optional text and an optional link for the right-side header.
        :raises ValueError: If right_header is not a dictionary or contains invalid keys.

        :return: dict: A dictionary containing the scraper's configuration.
        """

        if not isinstance(right_header, dict):
            raise ValueError("right_header must be a dictionary")

        valid_keys = {"text", "link"}
        if not all(key in valid_keys for key in right_header):
            raise ValueError("right_header can only contain 'text' and 'link' keys")

        if not readme or readme.strip() == "":
            readme = get_readme()

        self.config = {
            "title": title,
            "header_title": header_title,
            "description": description,
            "right_header": right_header,
            "readme": readme,
        }

    def create_controls(self, input_js):
        return ControlsAdapter.createControls(input_js)

    def get_controls(self, scraper_name):
        self.update_cache(scraper_name)

        return self.controls_cache[scraper_name]["controls"]

    def update_cache(self, scraper_name):
        scraper = self.get_scraper(scraper_name)
        input_js = scraper["input_js"]

        # Check if controls need to be recreated (i.e., if input_js has changed or if controls are not yet cached)
        if (
            scraper_name not in self.controls_cache
            or self.controls_cache[scraper_name]["input_js"] != input_js
        ):
            self.controls_cache[scraper_name] = {
                "input_js": input_js,
                "controls": self.create_controls(input_js),
            }

    def add_scraper(
        self,
        scraper_function,
        scraper_name=None,
        get_task_name=None,
        create_all_task=False,
        split_task=None,
        filters=[],
        sorts=[],
        views=[],
        remove_duplicates_by=None,
    ):
        if not hasattr(scraper_function, "_scraper_type"):
            raise ValueError(
                "The function must be a scraping function decorated with either @browser, @request or @task."
            )

        if scraper_function._scraper_type not in [
            ScraperType.REQUEST,
            ScraperType.BROWSER,
            ScraperType.TASK,
        ]:
            raise ValueError(
                f"Invalid scraper type: {scraper_function._scraper_type}. Must be 'browser', 'request' or 'task'."
            )

        if scraper_name is None:
            scraper_name = titlecase(scraper_function.__name__)

        if create_all_task and not callable(split_task):
            raise ValueError(
                "split_task function must be provided when create_all_task is True."
            )

        if not isinstance(filters, list):
            filters = [filters]
            

        if not isinstance(sorts, list):
            sorts = [sorts]


        if not isinstance(views, list):
            views = [views]
                                    
        # if not create_all_task and remove_duplicates_by:
        #     raise ValueError(
        #         "create_all_task must be True when remove_duplicates_by is provided."
        #     )        

        # Check for duplicate views
        view_ids = [view.id for view in views]
        if len(view_ids) != len(set(view_ids)):
            duplicate_view_ids = [id for id in view_ids if view_ids.count(id) > 1]
            raise ValueError(f"Duplicate views found: {duplicate_view_ids}")
        
        

        # Check for duplicate sorts
        sort_ids = [sort.id for sort in sorts]
        if len(sort_ids) != len(set(sort_ids)):
            duplicate_sort_ids = [id for id in sort_ids if sort_ids.count(id) > 1]
            raise ValueError(f"Duplicate sorts found: {duplicate_sort_ids}")

        is_default_found = False
        default_sort = None
        
        nosort = Sort(label='No Sort')
        nosort.id = 'no_sort'
        for sort in sorts:
            if sort.id == nosort.id:
                raise ValueError(f"Sort id '{nosort.id}' is reserved. Kindly use a different id.")
             
            if sort.is_default:
                if is_default_found:
                    nid  = sort.id
                    raise ValueError(f"More than one default sort ({default_sort}, {nid}) found. Kindly apply is_default sort on 1 Sort.")
                is_default_found = True
                default_sort = sort.id
        default_sort = default_sort if default_sort is not None else nosort.id
        nosort.is_default = default_sort == nosort.id
        sorts.insert(0, nosort)
        

        # Check for duplicate filters
        filter_ids = [filter_.id for filter_ in filters]
        if len(filter_ids) != len(set(filter_ids)):
            duplicate_filter_ids = [id for id in filter_ids if filter_ids.count(id) > 1]
            raise ValueError(f"Duplicate filters found: {duplicate_filter_ids}")

        scraper_name = scraper_function.__name__

        input_js = self.get_input_js(scraper_name)
        self.scrapers[scraper_name] = {
        "name": scraper_name,
        "input_js": input_js,
        "function": scraper_function,
        "scraper_name": scraper_name,
        "scraper_type": scraper_function._scraper_type,
        "get_task_name": get_task_name,
        "create_all_task": create_all_task,
        "split_task": split_task,
        "filters": filters,
        "sorts": sorts,
        "views": views,
        "default_sort": default_sort,  
        "remove_duplicates_by":remove_duplicates_by,
    }

    def get_scrapers_config(self):
        scraper_list = []
        for scraper_name, scraper in self.scrapers.items():
            input_js = self.get_input_js(scraper_name)
            input_js_hash = compute_hash(input_js)  # Compute the hash of input_js
            scraper["input_js"] = input_js

            views_json = [view.to_json() for view in scraper["views"]]
       
            default_sort = scraper["default_sort"]

            scraper_list.append(
                {
                    "name": scraper["name"],
                    "scraper_name": scraper_name,
                    "input_js": input_js,
                    "input_js_hash": input_js_hash,  # Include the input_js_hash in the result
                    "filters": [filter_.to_json() for filter_ in scraper["filters"]],
                    "sorts": [sort.to_json() for sort in scraper["sorts"]],
                    "views": views_json,
                    "default_sort": default_sort,                      
                }
            )
        return scraper_list

    def get_input_js(self, scraper_name):
        input_js_path = relative_path(f"backend/inputs/{scraper_name}.js")
        input_js = None
        if os.path.exists(input_js_path):
            with open(input_js_path, "r") as file:
                input_js = file.read()
        else:
            pth = f"backend/inputs/{scraper_name}.js"
            raise ValueError(
                f"Input js file not found for {scraper_name}. Kindly create {pth} file."
            )
        return input_js

    def get_scraping_function(self, scraper_name):
        return self.scrapers[scraper_name]["function"]

    def get_remove_duplicates_by(self, scraper_name):
        return self.scrapers[scraper_name]["remove_duplicates_by"]

    def get_scrapers_names(self):
        return list(self.scrapers.keys())

    def get_scraper(self, scraper_name):
        return self.scrapers[scraper_name]

    def get_browser_scrapers(self):
        return [
            name
            for name, scraper in self.scrapers.items()
            if scraper["scraper_type"] == ScraperType.BROWSER
        ]

    def get_task_scrapers(self):
        return [
            name
            for name, scraper in self.scrapers.items()
            if scraper["scraper_type"] == ScraperType.TASK
        ]

    def get_request_scrapers(self):
        return [
            name
            for name, scraper in self.scrapers.items()
            if scraper["scraper_type"] == ScraperType.REQUEST
        ]

    def set_rate_limit(self, browser=1, request=30, task=30):
        self.rate_limit["browser"] = inf if browser is None else browser
        self.rate_limit["request"] = inf if request is None else request
        self.rate_limit["task"] = inf if task is None else task

    def get_rate_limit(self):
        return self.rate_limit

    def enable_cache(self):
        self.cache = True

    def get_scraper(self, scraper_name):
        return self.scrapers.get(scraper_name)

    def create_tasks(self, scraper_name, data, metadata):
        scraper = self.scrapers[scraper_name]

        tasks = []

        create_all_tasks = scraper["create_all_task"]
        split_task = scraper["split_task"]

        if split_task:
            split_data = split_task(data)
            for item in split_data:
                task_name = (
                    scraper["get_task_name"](item)
                    if scraper["get_task_name"]
                    else "Unnamed Task"
                )
                tasks.append({"name": task_name, "data": item, "metadata": metadata})
        else:
            task_name = (
                scraper["get_task_name"](data)
                if scraper["get_task_name"]
                else "Unnamed Task"
            )
            tasks.append({"name": task_name, "data": data, "metadata": metadata})

        return tasks, bool(split_task), create_all_tasks

    def get_filters(self, scraper_name):
        return self.scrapers[scraper_name]["filters"]

    def get_sorts(self, scraper_name):
        return self.scrapers[scraper_name]["sorts"]

    def get_views(self, scraper_name):
        return self.scrapers[scraper_name]["views"]

    def get_default_sort(self, scraper_name):
        return self.scrapers[scraper_name]["default_sort"]

    def get_sort_ids(self, scraper_name):
        return [s.id for s in self.get_sorts(scraper_name)]

    def get_view_ids(self, scraper_name):
        return [v.id for v in self.get_views(scraper_name)]


Server = _Server()
