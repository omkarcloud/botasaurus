import os
import subprocess
import sys
import time
import click
from os import path, makedirs

@click.group()
def cli():
    """Botasaurus Kubernetes Cluster management CLI"""
    pass

def catch_file_not_found_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            print("You don't have gcloud installed on your system. Kindly install it.")
            sys.exit(1)
    return wrapper

WORKER_RAM_WITH_BROWSER = 1600
WORKER_RAM_WITHOUT_BROWSER = 800
WORKER_CPU = 1

def relative_path(path, goback=0):
    levels = [".."] * (goback + -1)
    return os.path.abspath(os.path.join(os.getcwd(), *levels, path.strip()))


def create_worker_depl_content(workers, ram, cpu):
    return f"""apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: worker-sts
spec:
  serviceName: worker-srv
  replicas: {workers}
  selector:
    matchLabels:
      app: worker
  template:
    metadata:
      labels:
        app: worker
    spec:
      containers:
        - name: worker
          command: ["python"]
          args: ["run.py", "backend"]
          resources:
            requests:
              memory: "{ram}Mi"
              cpu: "{cpu}m"
            limits:
              memory: "{ram}Mi"
              cpu: "{cpu}m"
          image: omkar/scraper:1.0.0
          ports:
            - containerPort: 8000
          env:
            - name: NODE_TYPE
              value: "WORKER"
---
apiVersion: v1
kind: Service
metadata:
  name: worker-srv
spec:
  selector:
    app: worker
  clusterIP: None
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
"""


def create_master_db_content(cluster_name):
    return """apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: master-db
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 4Gi
  storageClassName: standard-rwo
"""


def create_gke_content(cluster_name):
    return r"""name: Build and Deploy to GKE

on:
  push:
    branches:
      - master

env:
  ACTIONS_ALLOW_UNSECURE_COMMANDS: "true"
  GITHUB_PREV_SHA: ${{ github.event.before }}
  GITHUB_SHA: ${{ github.sha }}
  GKE_CLUSTER_NAME: GKE_CLUSTER_NAME_TEMPLATE
  GKE_PROJECT: ${{ secrets.GKE_PROJECT }}
  GKE_ZONE: us-central1-a
  USE_GKE_GCLOUD_AUTH_PLUGIN: "True"
jobs:
  setup-build-publish-deploy:
    name: Setup, Build, Publish, and Deploy
    runs-on: ubuntu-latest
    environment: production
    permissions:
      contents: "read"
      id-token: "write"

    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Set SCRAPER Enviroment Variable
        run: |
          echo "SCRAPER=$(echo "gcr.io/""$GKE_PROJECT""/scraper:""$GITHUB_SHA")" >> $GITHUB_ENV

      - name: Update Images
        run: |
          SCRAPER_ESCAPE=$(printf '%s\n' "$SCRAPER" | sed -e 's/[\/&]/\\&/g')
          sed -i -e 's/omkar\/scraper:1.0.0/'"$SCRAPER_ESCAPE"'/g' master-depl.yaml
          sed -i -e 's/omkar\/scraper:1.0.0/'"$SCRAPER_ESCAPE"'/g' worker-statefulset.yaml
        working-directory: k8s/app

      - name: Authenticate to Google Cloud
        uses: "google-github-actions/auth@v1"
        with:
          credentials_json: "${{ secrets.GKE_KEY }}"

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1

      - name: Configure Docker
        run: gcloud --quiet auth configure-docker

      - name: Build Image
        run: docker build --tag "$SCRAPER" .

      - name: Install GKE
        run: gcloud components install gke-gcloud-auth-plugin

      - name: Cluster Login
        run: gcloud container clusters get-credentials $GKE_CLUSTER_NAME --zone $GKE_ZONE --project $GKE_PROJECT

      - name: Delete Workers
        run: |
          kubectl delete statefulset worker-sts --ignore-not-found=true
          kubectl delete service worker-srv --ignore-not-found=true
        
      - name: Delete Previous Images
        run: for tag in $(gcloud container images list-tags gcr.io/$GKE_PROJECT/scraper --format='get(TAGS)' --limit=unlimited | sed 's/,/ /g'); do gcloud container images delete gcr.io/$GKE_PROJECT/scraper:$tag --quiet --project $GKE_PROJECT || true; done

      - name: Push Image
        run: docker push "$SCRAPER"          

      - name: Update Kubernetes Deployment Images
        run: |
          kubectl apply --recursive -f k8s/
          kubectl rollout status deployment/master-depl -w --timeout=60s || true
          kubectl get pods
""".replace(
        "GKE_CLUSTER_NAME_TEMPLATE", cluster_name
    )


def create_directory_if_not_exists(passed_path):
    dir_path = relative_path(passed_path, 0)
    if not path.exists(dir_path):
        makedirs(dir_path)


def create_file_with_content(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


@cli.command()
@click.option("--cluster-name", prompt="Enter cluster name", required=True, help="The name of the Kubernetes cluster to be created.")
@click.option(
    "--workers",
    prompt="Enter the number of workers to run. Default",
    default=3,
    type=int,
     help="The number of worker for the Kubernetes deployment. Defaults to 3."
)
@click.option(
    "--use-browser",
    prompt="Are browsers used in the scraper? [y/N]",
    required=True,
    type=bool,
    help="Specify if the scraper uses a browser, affects cpu and ram allocation.",
)
def build(cluster_name, workers, use_browser):
    """Creates the manifest files"""

    if workers <= 0:
        click.echo("The number of workers must be greater than 0.")
        return
    cluster_name = cluster_name.strip()

    worker_ram = WORKER_RAM_WITH_BROWSER if use_browser else WORKER_RAM_WITHOUT_BROWSER

    click.echo(
        f"------ Creating manifest files for cluster '{cluster_name}' with {workers} workers, where each worker node will have {worker_ram} RAM and {WORKER_CPU} CPU ------"
    )

    worker_cpu = WORKER_CPU * 1000

    # click.echo(f"worker nodes will have {worker_ram} RAM and {WORKER_CPU} CPU.")

    create_directory_if_not_exists("k8s")
    create_directory_if_not_exists("k8s/app")
    create_directory_if_not_exists("k8s/roles")
    create_directory_if_not_exists("k8s/volumes")
    create_directory_if_not_exists(".github")
    create_directory_if_not_exists(".github/workflows")

    # Constants for file content
    INGRESS_CONTENT = """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-service
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/proxy-body-size: 80m
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
spec:
  rules:
    - http:
        paths:
          # This triggers a 503 error and safeguards the API from unauthorized access to Kubernetes.
          - path: /api/k8s
            pathType: Prefix
            backend:
              service:
                name: default-http-backend
                port:
                  number: 80
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: master-srv
                port:
                  number: 8000
          - path: /
            pathType: Prefix
            backend:
              service:
                name: master-srv
                port:
                  number: 3000
"""
    MASTER_DEPL_CONTENT = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: master-depl
spec:
  replicas: 1
  strategy:
    type: Recreate  
  selector:
    matchLabels:
      app: master
  template:
    metadata:
      labels:
        app: master
    spec:
      volumes:
        - name: db
          persistentVolumeClaim:
            claimName: master-db
      containers:
        - name: master
          resources:
            requests:
              memory: "800Mi" 
              cpu: "1000m"              
            limits:
              memory: "800Mi"
              cpu: "1000m"           
          image: omkar/scraper:1.0.0
          volumeMounts:
            - mountPath: /db
              name: db
          ports:  
            - containerPort: 3000
              name: frontend
            - containerPort: 8000
              name: backend
          env:
            - name: NODE_TYPE
              value: "MASTER"
---
apiVersion: v1
kind: Service
metadata:
  name: master-srv
spec:
  selector:
    app: master
  ports:
    - name: frontend
      protocol: TCP
      port: 3000
      targetPort: 3000
    - name: backend
      protocol: TCP
      port: 8000
      targetPort: 8000
"""
    FULL_ACCESS_CONTENT = """kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: full-access
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: full-access
subjects:
  - kind: ServiceAccount
    name: default
    namespace: default
roleRef:
  kind: ClusterRole
  name: full-access
  apiGroup: rbac.authorization.k8s.io
"""
    master_db_content = create_master_db_content(cluster_name)
    worker_depl_content = create_worker_depl_content(workers, worker_ram, worker_cpu)
    gke_content = create_gke_content(cluster_name)

    app_dir = "k8s/app"
    roles_dir = "k8s/roles"
    volumes_dir = "k8s/volumes"
    workflows_dir = ".github/workflows"

    create_file_with_content(f"{app_dir}/ingress-srv.yaml", INGRESS_CONTENT)
    create_file_with_content(f"{app_dir}/master-depl.yaml", MASTER_DEPL_CONTENT)

    create_file_with_content(f"{app_dir}/worker-statefulset.yaml", worker_depl_content)

    create_file_with_content(f"{roles_dir}/full-access.yaml", FULL_ACCESS_CONTENT)

    create_file_with_content(f"{volumes_dir}/master-db.yaml", master_db_content)

    create_file_with_content(f"{workflows_dir}/gke.yaml", gke_content)

    click.echo(f"Successfully created manifest files.")


def get_first_line(data):
    ls = data.strip().splitlines()
    first_line = ls[0].strip() if ls else None
    return first_line


def get_all_lines(data):
    ls = data.strip().splitlines()
    if ls:
        return [l.strip() for l in ls]
    else:
        return []

@catch_file_not_found_error
def get_project_id():
    result = subprocess.run(
        ["gcloud", "projects", "list", "--format=value(projectId)", "--limit=1"],
        check=True,
        capture_output=True,
        text=True,
    )
    return get_first_line(result.stdout)


def get_cluster_external_ip(cluster_name, region, project_id):
    ip_address_result = subprocess.run(
        [
            "gcloud",
            "compute",
            "addresses",
            "describe",
            create_ip_name(cluster_name),
            "--region",
            region,
            "--project",
            project_id,
            "--format=value(address)",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return get_first_line(ip_address_result.stdout)


def create_ip_name(cluster_name):
    return f"{cluster_name}-ip"


def get_cluster_status(cluster_name, zone, project_id):
    result = subprocess.run(
        [
            "gcloud",
            "container",
            "clusters",
            "describe",
            cluster_name,
            "--zone",
            zone,
            "--project",
            project_id,
            "--format=value(status)",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return get_first_line(result.stdout)





def get_cluster_names(project_id):
    result = subprocess.run(
        [
            "gcloud",
            "container",
            "clusters",
            "list",
            "--format=value(name)",
            "--project",
            project_id,
            "--limit=unlimited",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return get_all_lines(result.stdout)


def list_all_ips(project_id, region):
    result = subprocess.run(
        [
            "gcloud",
            "compute",
            "addresses",
            "list",
            "--format=value(name)",
            "--project",
            project_id,
            "--regions",
            region,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return get_all_lines(result.stdout)


DEFAULT_INSTANCE = "e2-small"


def run_create_cluster_command(cluster_name, zone, project_id, max_nodes):
    command = f"""gcloud beta container --project "{project_id}" clusters create "{cluster_name}" --no-enable-basic-auth --cluster-version "1.27.8-gke.1067004" --release-channel "regular" --machine-type "{DEFAULT_INSTANCE}" --image-type "COS_CONTAINERD" --disk-type "pd-balanced" --disk-size "20" --metadata disable-legacy-endpoints=true --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --num-nodes "{max_nodes}" --logging=SYSTEM,WORKLOAD --monitoring=SYSTEM --enable-ip-alias --network "projects/{project_id}/global/networks/default" --subnetwork "projects/{project_id}/regions/us-central1/subnetworks/default" --no-enable-intra-node-visibility --default-max-pods-per-node "110" --security-posture=standard --workload-vulnerability-scanning=disabled --no-enable-master-authorized-networks --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver --enable-autoupgrade --enable-autorepair --max-surge-upgrade 1 --max-unavailable-upgrade 0 --binauthz-evaluation-mode=DISABLED --enable-managed-prometheus --enable-shielded-nodes --node-locations {zone} --zone {zone} """
    subprocess.run(command, shell=True, check=True, stderr=subprocess.STDOUT)


def delete_external_ip(cluster_name, region, project_id):
    try:
        subprocess.run(
            [
                "gcloud",
                "compute",
                "addresses",
                "delete",
                f"{cluster_name}-ip",
                "--region",
                region,
                "--project",
                project_id,
                "--quiet",
            ],
            check=True,
            stderr=subprocess.STDOUT,
            text=True,
        )

    except subprocess.CalledProcessError as e:
        if "was not found" in e.stderr:
            pass  # Deletion was already considered successful
        else:
            raise e  # Re-raise the exception for other errors


def enable_gcloud(project_id):
    subprocess.run(
        [
            "gcloud",
            "services",
            "enable",
            "artifactregistry.googleapis.com",
            "container.googleapis.com",
            "compute.googleapis.com",
            "--project",
            project_id,
        ],
        check=True,
        stderr=subprocess.STDOUT,
    )  # Modification here


def delete_scraper_images(project_id):
    method = "delete"
    command = f"""for tag in $(gcloud container images list-tags gcr.io/{project_id}/scraper --format='get(TAGS)' --limit=unlimited | sed 's/,/ /g'); do gcloud container images {method} gcr.io/{project_id}/scraper:$tag --quiet --project {project_id} || true; done"""
    subprocess.run(command, shell=True, check=True)


def get_cluster_credentials(cluster_name, zone, project_id):
    click.echo("Getting cluster credentials...")
    subprocess.run(
        [
            "gcloud",
            "container",
            "clusters",
            "get-credentials",
            cluster_name,
            "--zone",
            zone,
            "--project",
            project_id,
        ],
        check=True,
        stderr=subprocess.STDOUT,
    )


def cluster_exists(cluster_name, project_id):
    cluster_names = get_cluster_names(project_id)
    return cluster_name in cluster_names


def check_ip_exists(cluster_name, project_id, region):
    ips = list_all_ips(project_id, region)
    return create_ip_name(cluster_name) in ips


def perform_create_cluster(cluster_name, max_nodes):
    project_id = get_project_id()

    # TODO: maybe determine based on nearest country best. allow config as well.
    zone = "us-central1-a"
    region = "us-central1"

    enable_gcloud(project_id)

    if not cluster_exists(cluster_name, project_id):
        click.echo("Creating cluster...")
        run_create_cluster_command(cluster_name, zone, project_id, max_nodes)

        while True:
            result = get_cluster_status(cluster_name, zone, project_id)
            status = result
            if status == "RUNNING":
                break
            time.sleep(2)

    # Usage:
    if not check_ip_exists(cluster_name, project_id, region):
        # Create an external IP address
        click.echo("Getting IP address...")

        subprocess.run(
            [
                "gcloud",
                "compute",
                "addresses",
                "create",
                f"{cluster_name}-ip",
                "--region",
                region,
                "--project",
                project_id,
            ],
            check=True,
            stderr=subprocess.STDOUT,
        )

    ip_address = get_cluster_external_ip(cluster_name, region, project_id)

    get_cluster_credentials(cluster_name, zone, project_id)

    click.echo("Enabling nginx load balancer...")

    # Add the ingress-nginx repository
    subprocess.run(
        [
            "helm",
            "repo",
            "add",
            "ingress-nginx",
            "https://kubernetes.github.io/ingress-nginx",
        ],
        check=True,
        stderr=subprocess.STDOUT,
    )


    # Update the ingress-nginx repository
    subprocess.run(
        [
            "helm",
            "repo",
            "update"
        ],
        check=True,
        stderr=subprocess.STDOUT,
    )

    # Install or upgrade the ingress-nginx chart with the external IP
    subprocess.run(
        [
            "helm",
            "upgrade",
            "--install",
            "ingress-nginx-chart",
            "ingress-nginx/ingress-nginx",
            "--set",
            f"controller.service.loadBalancerIP={ip_address}",
            "--set",
            "controller.service.externalTrafficPolicy=Local",
        ],
        check=True,
        stderr=subprocess.STDOUT,
    )

    return ip_address


def delete_pvc_if_exists(pvc_name):
    """Deletes the specified PVC only if it exists, then waits for its deletion."""
    result = subprocess.run(
        ["kubectl", "get", "pvc", pvc_name], capture_output=True, text=True
    )

    if result.returncode == 0:
        click.echo("Deleting the database...")

        subprocess.run(["kubectl", "delete", "pvc", pvc_name], check=True)

        click.echo("Waiting for the deletion of database...")
        subprocess.run(
            ["kubectl", "wait", "--for=delete", f"pvc/{pvc_name}", "--timeout=300s"],
            check=True,
        )


def perform_delete_cluster(cluster_name):
    project_id = get_project_id()
    zone = "us-central1-a"
    region = "us-central1"

    has_cluster = cluster_exists(cluster_name, project_id)
    if has_cluster:

        get_cluster_credentials(cluster_name, zone, project_id)

        # Delete the Deployment
        subprocess.run(
            [
                "kubectl",
                "delete",
                "deployment",
                "master-depl",
                "--grace-period=0",
                "--force",
                "--ignore-not-found=true",
            ],
            check=True,
            stderr=subprocess.STDOUT,
        )

        delete_pvc_if_exists("master-db")

    click.echo("Deleting Images...")

    delete_scraper_images(project_id)

    if check_ip_exists(cluster_name, project_id, region):
        # Delete the external IP address associated with the cluster
        click.echo("Deleting IP address...")
        delete_external_ip(cluster_name, region, project_id)

    if has_cluster:
        click.echo("Deleting the cluster...")
        # Delete the cluster
        subprocess.run(
            [
                "gcloud",
                "container",
                "clusters",
                "delete",
                cluster_name,
                "--zone",
                zone,
                "--project",
                project_id,
                "--quiet",
            ],
            check=True,
            stderr=subprocess.STDOUT,
        )


@cli.command()
@click.option("--cluster-name", prompt="Enter cluster name", required=True, help="The name of the Kubernetes cluster to be created.")
@click.option(
    "--nodes",
    prompt="Enter the maximum number of nodes to run in the cluster (default: 3). Keep in mind that, based on the GCP quota, there is a default limit of 3 nodes. You may need to request a quota increase if you want to create clusters with more nodes.",
    default=3,
    type=int,
    help="Maximum number of nodes for the cluster. Defaults to 3. Adjust based on requirements and GCP quota."
)
def create_cluster(cluster_name, nodes):
    """Create the cluster"""
    if nodes <= 0:
        click.echo("The number of nodes must be greater than 0.")
        return
    cluster_name = cluster_name.strip()

    click.echo(f"------ Creating cluster {cluster_name} ------")

    ip_address = perform_create_cluster(cluster_name, nodes)
    click.echo(f"Successfully created cluster.")

    click.echo("Next steps:")
    click.echo("1. Deploy the Scraper using Github Actions.")
    click.echo("2. Visit http://{}/ to access it.".format(ip_address))


@cli.command()
@click.option("--cluster-name", prompt="Enter cluster name", required=True, help="The name of the Kubernetes cluster to delete.")
@click.option(
    "--force", is_flag=True, help="Force deletion of the cluster without confirmation. Use this option with caution."
)
def delete_cluster(cluster_name, force):
    """Deletes the cluster"""
    cluster_name = cluster_name.strip()
    if not force:  # Ask for confirmation if --force is not used
        if not click.confirm(
            f"Are you sure you want to delete cluster '{cluster_name}'? This will permanently delete the entire database in '{cluster_name}'! If you need the data, please download it before proceeding."
        ):
            click.echo("Deletion aborted.")
            sys.exit(1)
            return  # Exit if the user doesn't confirm

    click.echo(f"------ Deleting cluster {cluster_name} ------")
    perform_delete_cluster(cluster_name)

    click.echo(f"Successfully deleted cluster.")


if __name__ == "__main__":
    cli()
    # Usage examples:
    # 1. python -m botasaurus_server build --cluster-name omkar --workers 1 --use-browser true
    # 2. python -m botasaurus_server create-cluster --cluster-name omkar --nodes 1
    # 3. python -m botasaurus_server delete-cluster --cluster-name omkar --force
