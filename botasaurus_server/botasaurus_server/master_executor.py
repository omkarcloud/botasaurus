from threading import Lock
from .task_executor import TaskExecutor
from .server import Server
from .k8s import K8s

class MasterExecutor(TaskExecutor):

    def load(self):
        self.lock = Lock()
        self.k8s = K8s()
        # Initialize capacities
        self.current_capacity = {"request": 0, "browser": 0, "task": 0}
        self.max_capacity = self.calculate_max_capacity()

    def get_max_running_count(self, scraper_type):
        return self.max_capacity[scraper_type]

    def get_current_running_count(self, scraper_type):
        return self.current_capacity[scraper_type]

    def run_task_and_update_state(self, scraper_type, task_json):
            node = self.k8s.get_min_capacity_node(scraper_type) 

            # Send task to the selected node
            self.k8s.run_task_on_node(task_json, node['node_name'])

            # Update capacities
            self.increment_master_capacity(node, scraper_type)

    def increment_master_capacity(self, node , scraper_type):
        with self.lock:
            node['current_capacity'][scraper_type] += 1
            self.current_capacity[scraper_type] += 1

    def decrement_master_capacity(self,  node , scraper_type):
        with self.lock:
            node['current_capacity'][scraper_type] -= 1
            self.current_capacity[scraper_type] -= 1

    def calculate_max_capacity(self):
        limit = Server.get_rate_limit()
        replicas = len(self.k8s.nodes)
        return {"request": limit["request"] * replicas,"task": limit["task"] * replicas, "browser": limit["browser"] * replicas}

    def on_success(self, task_id, task_type, task_result, node_name):
        node = self.k8s.get_node(node_name)
        self.decrement_master_capacity(node, task_type)

        # Further processing of task_result can be done here
        self.mark_task_as_success(task_id, task_result, Server.cache)
        self.update_parent_task(task_id)
    
    def on_failure(self, task_id, task_type, task_result, node_name):
        node = self.k8s.get_node(node_name)
        self.decrement_master_capacity(node, task_type)
        
        # Further processing of task_result can be done here
        self.mark_task_as_failure(task_id, task_result)
        self.update_parent_task(task_id)
