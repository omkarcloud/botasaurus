from time import sleep
from kubernetes import config
from kubernetes.client import CoreV1Api, ApiClient, AppsV1Api
import requests
import traceback
from .env import is_in_kubernetes

class K8s:
    def __init__(self):

        if is_in_kubernetes:
            config.load_incluster_config()
        else:
            config.load_kube_config()

        self.cl = ApiClient()
        self.app_api = AppsV1Api(self.cl)
        self.k8s_api = CoreV1Api(self.cl)
        self.pod_type = "worker"
        self.wait_for_workers()
        self.nodes = self.get_worker_nodes()

    def wait_for_workers(self):
        ready_workers = 0
        total_workers = 0
        while not total_workers:
            try:
                total_workers = self.get_worker_count()
                if total_workers:
                    break
            except Exception as e:
                print(f"An exception occurred: {str(e)}")
                traceback.print_exc()
            sleep(1)
        while ready_workers < total_workers:
            try:
                ready_workers = self.get_ready_worker_count()
                if not (ready_workers < total_workers):
                    break

                print(f"Only {ready_workers} out of {total_workers} Workers are ready. Waiting for all Workers to be ready.")
                sleep(1)
            except Exception as e:
                print(f"An exception occurred: {str(e)}")
                traceback.print_exc()

        print("All Workers are ready!")

    def get_worker_count(self):
        depl = self.app_api.read_namespaced_stateful_set(name=self.pod_type + "-sts", namespace="default")
        return depl.spec.replicas

    def get_min_capacity_node(self, scraper_type):
        return min(self.nodes, key=lambda x: x['current_capacity'][scraper_type])

    def get_node(self, node_name):
        return next(node for node in self.nodes if node['node_name'] == node_name)

    def get_ready_worker_count(self):
        ready_count = 0
        pods = self.k8s_api.list_namespaced_pod(namespace="default", label_selector="app=" + self.pod_type )
        for pod in pods.items:
            if pod.status.phase == "Running" and all([c.ready for c in pod.status.container_statuses]):
                ready_count += 1
        return ready_count

    def get_worker_nodes(self):
        pods = self.k8s_api.list_namespaced_pod(namespace="default", label_selector="app=" + self.pod_type )
        nodes = []
        for pod in pods.items:
            node = {"node_name": pod.metadata.name, "current_capacity": {"request": 0, "browser": 0, "task": 0}}
            nodes.append(node)
        return nodes
        
    def run_task_on_node(self, task, node_name):
        url = f"http://{node_name}.worker-srv.default.svc.cluster.local:8000/k8s/run-worker-task"
        payload = {"task": task, "node_name": node_name}
        response = requests.post(url, json=payload)
        response.raise_for_status()
if __name__ == "__main__":
    K8s()    