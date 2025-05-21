import os
import subprocess
import sys
import time
import click
from os import path, makedirs

from .package_storage import get_package_storage
from .vm import extractRepositoryName, install_desktop_app_in_vm, install_scraper_in_vm, install_ui_scraper_in_vm

@click.group(context_settings=dict(max_content_width=160))
def cli():
    """Botasaurus CLI"""
    pass

def relative_path(path, goback=0):
    levels = [".."] * (goback + -1)
    return os.path.abspath(os.path.join(os.getcwd(), *levels, path.strip()))


def create_ip_name(cluster_name):
    return f"{cluster_name}-ip"


def create_directory_if_not_exists(passed_path):
    dir_path = relative_path(passed_path, 0)
    if not path.exists(dir_path):
        makedirs(dir_path)


def catch_gcloud_not_found_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            print("You don't have gcloud installed on your system. Kindly install it.")
            sys.exit(1)
    return wrapper


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

WORKER_RAM_WITH_BROWSER = 4000
WORKER_RAM_WITHOUT_BROWSER = 800
WORKER_CPU = 1



def create_worker_depl_content(workers, ram, cpu, use_browser):
    if not use_browser:
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
          volumeMounts:
            - name: dshm
              mountPath: /dev/shm
          ports:
            - containerPort: 8000
          env:
            - name: NODE_TYPE
              value: "WORKER"
      volumes:
        - name: dshm
          emptyDir:
            medium: Memory
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

on: push

env:
  ACTIONS_ALLOW_UNSECURE_COMMANDS: "true"
  GITHUB_PREV_SHA: ${{ github.event.before }}
  GITHUB_SHA: ${{ github.sha }}
  GKE_CLUSTER_NAME: GKE_CLUSTER_NAME_TEMPLATE
  GKE_PROJECT: ${{ secrets.GKE_PROJECT }}
  GKE_ZONE: GKE_ZONE_TEMPLATE
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
    ).replace("GKE_ZONE_TEMPLATE", get_zone())


def create_file_with_content(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def exit_if_err(result):
    if result.stderr:
      print(result.stderr)
      raise Exception("Command failed with above error.")

@catch_gcloud_not_found_error
def project_exists(project_id):
    try:
        # Execute the gcloud command to describe the project
        result = subprocess.run(
            ["gcloud", "projects", "describe", project_id, "--format=value(projectId)"],
            check=False,  # Do not raise exception on non-zero exit
            capture_output=True,  # Capture the output and error
            text=True  # Return output and error as string
        )

        # If the command executed successfully and the output contains the project ID, the project exists
        if result.returncode == 0 and project_id in result.stdout.strip():
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred while checking the project: {e}")
        return False

def set_and_get_project_id():
    project_ids = get_project_ids()
    if len(project_ids) == 0:
        click.echo("No GCP projects found. Please create a project first.")
        sys.exit(1)
    elif len(project_ids) == 1:
        fitem = project_ids[0]
        get_package_storage().set_item("project_id", fitem)
        click.echo(f"Selected {fitem} project.")
        return fitem
    else:
        click.echo("Multiple projects found. Please select one:")
        for idx, project_id in enumerate(project_ids):
            click.echo(f"{idx + 1}: {project_id}")
        while True:
            selection = click.prompt("Enter the number of the project you want to use", type=int)
            if 1 <= selection <= len(project_ids):
                selected_project_id = project_ids[selection - 1]
                get_package_storage().set_item("project_id", selected_project_id)
                return selected_project_id
            else:
                click.echo("Invalid selection. Please select a number from the list.")

@catch_gcloud_not_found_error
def get_project_id():
    project_id = get_package_storage().get_item("project_id")
    if project_id:
        if project_exists(project_id):
            return project_id
    
    pj =  set_and_get_project_id()
    click.echo(f"You have selected {pj} project.")
    return pj

@catch_gcloud_not_found_error
def get_project_ids():
    result = subprocess.run(["gcloud", "projects", "list", "--format=value(projectId)"],
        check=False, capture_output=True, text=True)
    exit_if_err(result)
    return get_all_lines(result.stdout)

def set_get_region():
      get_package_storage().remove_item("region")
      all_regions = ["us-central1","us-east1","us-east4","us-east5","us-south1","us-west1","us-west2","us-west3","us-west4","africa-south1","asia-east1","asia-east2","asia-northeast1","asia-northeast2","asia-northeast3","asia-south1","asia-south2","asia-southeast1","asia-southeast2","australia-southeast1","australia-southeast2","europe-central2","europe-north1","europe-southwest1","europe-west1","europe-west10","europe-west12","europe-west2","europe-west3","europe-west4","europe-west6","europe-west8","europe-west9","me-central1","me-central2","me-west1","northamerica-northeast1","northamerica-northeast2","southamerica-east1","southamerica-west1"]
      click.echo("Please choose datacenter region:")
      for i, region in enumerate(all_regions, start=1):
          click.echo(f"{i}. {region}")
      while True:
          selection = click.prompt("Enter the number of the region to use. Defaults to us-central1", type=int, default=1)
          if 1 <= selection <= len(all_regions):
              selected_region = all_regions[selection - 1]
              get_package_storage().set_item("region", selected_region)
              return selected_region
          else:
              click.echo("Invalid selection. Please select a number from the list.")
    
def get_region():
   region = get_package_storage().get_item("region")
   if not region:
       rgn =  set_get_region()
       click.echo(f"You have selected {rgn} region.")
       return rgn
   return region

def get_zone():
   region = get_region()
   return f"{region}-a"

def get_regional_ip_details(cluster_name, region, project_id):
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

def format_clusters(clusters):
    formatted_clusters = []
    for cluster in clusters:
        name, location = cluster.split()
        formatted_clusters.append({"name": name, "location": location})
    return formatted_clusters

def get_cluster_zone(cluster_name, project_id):
    result = subprocess.run(
        [
            "gcloud",
            "container",
            "clusters",
            "list",
            "--format=value(name,locations[0])",
            "--project",
            project_id,
            "--limit=unlimited",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    ls =  format_clusters(get_all_lines(result.stdout))
    for x in ls:
        if x['name']  == cluster_name:
            return x['location']
    raise Exception("Cluster not found.")


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


def list_all_ips_regional(project_id, region):
    commands = [
        "gcloud",
        "compute",
        "addresses",
        "list",
        "--format=value(name)",
        "--project",
        project_id,
        "--regions",
        region,
        "--quiet",
    ]

    result = invoke_shell_command(commands, project_id)

    return get_all_lines(result.stdout)


def enable_compute_services(project_id):
    click.echo("Enabling compute services...")
    subprocess.run(
        [
            "gcloud",
            "services",
            "enable",
            "compute.googleapis.com",
            "--project",
            project_id,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
def invoke_shell_command(commands, project_id):
    try:

        return subprocess.run(
            commands,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        if "Enable it by visiting https://console.developers" in e.stderr:
            enable_compute_services(project_id)
            return invoke_shell_command(commands, project_id)
        else:
            raise e  # Re-raise the exception for other errors



def create_cluster_command_string(cluster_name, rgn, zone, project_id, max_nodes, machine_type):
    num_nodes = max_nodes
    command = f"""gcloud beta container --project "{project_id}" clusters create "{cluster_name}" --no-enable-basic-auth --release-channel "regular" --machine-type "{machine_type}" --image-type "COS_CONTAINERD" --disk-type "pd-balanced" --disk-size "30" --metadata disable-legacy-endpoints=true --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --num-nodes "{num_nodes}" --logging=SYSTEM,WORKLOAD --monitoring=SYSTEM --enable-ip-alias --network "projects/{project_id}/global/networks/default" --subnetwork "projects/{project_id}/regions/{rgn}/subnetworks/default" --no-enable-intra-node-visibility --default-max-pods-per-node "110" --security-posture=standard --workload-vulnerability-scanning=disabled --no-enable-master-authorized-networks --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver --enable-autoupgrade --enable-autorepair --max-surge-upgrade 1 --max-unavailable-upgrade 0 --binauthz-evaluation-mode=DISABLED --enable-managed-prometheus --enable-shielded-nodes --node-locations {zone} --zone {zone}"""
    return command

def perform_create_cluster_commands(cluster_name, rgn,zone, project_id, max_nodes, machine_type):
    command = create_cluster_command_string(cluster_name, rgn,zone, project_id, max_nodes, machine_type)
    subprocess.run(command, shell=True, check=True, stderr=subprocess.STDOUT)


def delete_external_ip_regional(cluster_name,  project_id, region):
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

def enable_gcloud_services(project_id):
    click.echo("Enabling services...")
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
    ) 


def has_images(project_id):
    command = f"gcloud container images list-tags gcr.io/{project_id}/scraper --format='get(TAGS)' --limit=1"
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)

    # Check if the command output (stdout) is not empty, indicating the presence of at least one image tag.
    if result.stdout.strip():
        return True
    else:
        return False

def delete_scraper_images(project_id):
    method = "delete"
    command = f"""for tag in $(gcloud container images list-tags gcr.io/{project_id}/scraper --format='get(TAGS)' --limit=unlimited | sed 's/,/ /g'); do gcloud container images {method} gcr.io/{project_id}/scraper:$tag --quiet --project {project_id} || true; done"""
    # shows a red error if no images, hence hide the output.
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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

def does_ip_exists_regional(cluster_name, project_id, region):
    ips = list_all_ips_regional(project_id, region)
    return create_ip_name(cluster_name) in ips

def run_create_cluster_commands(cluster_name, max_nodes, machine_type):
    project_id = get_project_id()

    region = get_region()
    zone =get_zone()

    enable_gcloud_services(project_id)
    skipped = False
    if cluster_exists(cluster_name, project_id):
        click.echo(f"Cluster '{cluster_name}' already exists.")
        if click.confirm("Do you want to delete the existing cluster and create a new one?"):
            perform_cluster_deletion(cluster_name, True)
        else:
            click.echo("Skipping cluster creation.")
            skipped = True

    if not skipped:
      click.echo("------------")
      click.echo(f"Creating cluster '{cluster_name}' with the following configuration:")
      click.echo(f"    - Workers: {max_nodes}")
      if machine_type == DEFAULT_INSTANCE:
          click.echo(f"    - Worker resources: {7.5} GB RAM, {2} CPU each")
      click.echo(f"    - Persistent volume: 4GB for storing scraper output")
      click.echo("------------")

      perform_create_cluster_commands(cluster_name, region, zone, project_id, max_nodes, machine_type)

      while True:
          result = get_cluster_status(cluster_name, zone, project_id)
          status = result
          if status == "RUNNING":
              break
          else:
              click.echo("Waiting for the cluster to be up...")
              time.sleep(2)
        
    # Usage:
    if not does_ip_exists_regional(cluster_name, project_id, region):
        # Create an external IP address
        click.echo("Creating IP address...")

        create_external_ip_regional(cluster_name, project_id, region)
    else:
        click.echo("Skipping IP address creation as it already exists.")

    ip_address = get_regional_ip_details(cluster_name, region, project_id)

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


def create_external_ip_regional(cluster_name, project_id, region):
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


def delete_pvc_if_exists(pvc_name):
    """Deletes the specified PVC only if it exists, then waits for its deletion."""
    result = subprocess.run(
        ["kubectl", "get", "pvc", pvc_name], capture_output=True, text=True
    )

    if result.returncode == 0:

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
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        click.echo("Deleting the database...")

        subprocess.run(["kubectl", "delete", "pvc", pvc_name],             check=True,
            stderr=subprocess.STDOUT,
)

        click.echo("Waiting for the deletion of database...")
        subprocess.run(
            ["kubectl", "wait", "--for=delete", f"pvc/{pvc_name}", "--timeout=300s"],
                        check=True,
            stderr=subprocess.STDOUT,

        )


DEFAULT_INSTANCE = "n1-standard-2"

@cli.command()
@click.option("--name", prompt="Enter VM name", required=True, help="The name of the VM where to create the IP address.")
def create_ip(name):
    """Creates an IP address for a VM"""
    project_id = get_project_id()
    name = name.strip().rstrip('-ip')
    region = get_region()

    if does_ip_exists_regional(name, project_id, region):
        click.echo(f"IP address {name}-ip already exists.")
    else:
        click.echo(f"------ Creating IP address {name} ------")
        create_external_ip_regional(name, project_id, region)
        click.echo("Successfully created IP address.")

@cli.command()
@click.option("--name", prompt="Enter VM name", required=True, help="The name of the VM to delete the IP address for.")
@click.option(
    "--force", is_flag=True, help="Force deletion of the IP address without confirmation. Use this option with caution."
)
def delete_ip(name, force):
    """Deletes an IP address for a VM"""
    project_id = get_project_id()
    name = name.strip().rstrip('-ip')
    region = get_region()
    if not does_ip_exists_regional(name, project_id, region):
        ips = list_all_ips_regional(project_id, region)
        if ips:
          ips = ', '.join(ips)
          click.echo(f"IP address {name}-ip not found. Available IP addresses are: {ips}.")
        else: 
          click.echo(f"IP address {name}-ip not found.")
        return

    if not force:
        if not click.confirm(f"Are you sure you want to delete the IP address '{name}'?"):
            click.echo("Deletion aborted.")
            return

    click.echo(f"------ Deleting IP address {name} ------")

    delete_external_ip_regional(name,  project_id, region) 
    click.echo("Successfully deleted IP address.")

@cli.command()
@click.option("--cluster-name", prompt="Enter cluster name", required=True, help="The name of the Kubernetes cluster to be created.")
@click.option("--machine-type", prompt=f"Enter machine type. Default", default=DEFAULT_INSTANCE, help=f"Specify the GCP machine type to create. Defaults to {DEFAULT_INSTANCE}.")
@click.option(
    "--number-of-machines",
    prompt="Enter the maximum number of machines to run in the cluster (default: 2). Keep in mind that, based on the GCP quota, You may need to request a quota increase if you want to create clusters with more machines.",
    default=2,
    type=int,
    help="Maximum number of machines in the cluster. Defaults to 2. Adjust based on requirements and GCP quota."
)
def create_cluster(cluster_name, machine_type, number_of_machines):
    """Create the cluster"""
    if number_of_machines <= 0:
        click.echo("The number of machines must be greater than 0.")
        return
    
    cluster_name = cluster_name.strip()
    machine_type = machine_type.strip()

    click.echo("------------")
    click.echo(f"Creating cluster '{cluster_name}' with the following components:")
    click.echo(f"    - {number_of_machines} machines of type {machine_type}")
    click.echo(f"    - A static IP address")
    click.echo("------------")

    ip_address = run_create_cluster_commands(cluster_name, number_of_machines, machine_type)
    click.echo(f"Hurray! You have successfully created the cluster.")

    click.echo("Your Next steps are as follows:")
    click.echo("1. Deploy the Scraper using Github Actions.")
    click.echo("2. Then, wait 5 minutes for the cluster to fully deploy.")
    click.echo("3. Visit http://{}/ to use the Scraper.".format(ip_address))

@cli.command(help='Creates the manifest files for Kubernetes deployment and GitHub Actions')
@click.option("--cluster-name", prompt="Enter cluster name", required=True, help="The name of the Kubernetes cluster to be created.")
@click.option(
    "--workers",
    prompt="Enter the number of workers to run. Default",
    default=1,
    type=int,
     help="The number of worker for the Kubernetes deployment. Defaults to 1."
)
@click.option(
    "--use-browser",
    prompt="Are browsers used in the scraper? [y/N]",
    required=True,
    type=bool,
    help="Specify if the scraper uses a browser, affects cpu and ram allocation.",
)
def create_manifests(cluster_name, workers, use_browser):

    if workers <= 0:
        click.echo("The number of workers must be greater than 0.")
        return
    cluster_name = cluster_name.strip()

    worker_ram = WORKER_RAM_WITH_BROWSER if use_browser else WORKER_RAM_WITHOUT_BROWSER

    click.echo("------------")
    click.echo(f"Creating manifest files for cluster '{cluster_name}' with the following configuration:")
    click.echo(f"    - Workers: {workers}") 
    click.echo(f"    - Worker resources: {worker_ram} GB RAM, {WORKER_CPU} CPU each")
    click.echo(f"    - Persistent volume: 4GB for storing scraper output")
    click.echo("------------")


    worker_cpu = WORKER_CPU * 1000

    # click.echo(f"worker nodes will have {worker_ram} RAM and {WORKER_CPU} CPU.")

    create_directory_if_not_exists("k8s")
    create_directory_if_not_exists("k8s/app")
    create_directory_if_not_exists("k8s/roles")
    create_directory_if_not_exists("k8s/volumes")
    create_directory_if_not_exists(".github")
    create_directory_if_not_exists(".github/workflows")

    # Constants for file content
    ip_name = create_ip_name(cluster_name)
    # Constants for file content
    INGRESS_CONTENT = f"""apiVersion: networking.k8s.io/v1
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
    worker_depl_content = create_worker_depl_content(workers, worker_ram, worker_cpu, use_browser)
    gke_content = create_gke_content(cluster_name)

    app_dir = "k8s/app"
    roles_dir = "k8s/roles"
    volumes_dir = "k8s/volumes"
    workflows_dir = ".github/workflows"

    create_file_with_content(f"{app_dir}/ingress.yaml", INGRESS_CONTENT)
    create_file_with_content(f"{app_dir}/master-depl.yaml", MASTER_DEPL_CONTENT)

    create_file_with_content(f"{app_dir}/worker-statefulset.yaml", worker_depl_content)

    create_file_with_content(f"{roles_dir}/full-access.yaml", FULL_ACCESS_CONTENT)

    create_file_with_content(f"{volumes_dir}/master-db.yaml", master_db_content)

    create_file_with_content(f"{workflows_dir}/gke.yaml", gke_content)

    click.echo(f"Successfully created manifest files.")
def get_region_from_zone(zone):
    """
    Returns the region for a given GCP zone.

    Args:
        zone (str): The GCP zone, e.g. "us-central1-a".

    Returns:
        str: The corresponding region, e.g. "us-central1".
    """
    # Split the zone string on the hyphen
    zone_parts = zone.split('-')

    # The region is everything except the last part (the zone)
    region = '-'.join(zone_parts[:-1])

    return region

def run_delete_cluster_commands(cluster_name):
    project_id = get_project_id()
    region = get_region()
    zone = get_zone()

    has_cluster = cluster_exists(cluster_name, project_id)
    if has_cluster:
        zone = get_cluster_zone(cluster_name, project_id)
        region = get_region_from_zone(zone)
        if get_cluster_status(cluster_name, zone, project_id) == "RUNNING":
          get_cluster_credentials(cluster_name, zone, project_id)
          delete_pvc_if_exists("master-db")

    if has_images(project_id):
      click.echo("Deleting Images...")
      delete_scraper_images(project_id)
    else:
      click.echo("Skipping image deletion as no images exists.")
    if does_ip_exists_regional(cluster_name, project_id, region):
        # Delete the external IP address associated with the cluster
        click.echo("Deleting IP address...")
        delete_external_ip_regional(cluster_name,  project_id, region)
    else:
        click.echo("Skipping IP address deletion as it does not exist.")

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
        return False
    else:
        click.echo("Skipping cluster deletion as it does not exist.")
        return True

@cli.command()
@click.option("--cluster-name", prompt="Enter cluster name", required=True, help="The name of the Kubernetes cluster to delete.")
@click.option(
    "--force", is_flag=True, help="Force deletion of the cluster without confirmation. Use this option with caution."
)
def delete_cluster(cluster_name, force):
    """Deletes the cluster"""
    perform_cluster_deletion(cluster_name, force)

def perform_cluster_deletion(cluster_name, force):
    cluster_name = cluster_name.strip()
    if not force:  # Ask for confirmation if --force is not used
        if not click.confirm(
            f"Are you sure you want to delete cluster '{cluster_name}'? This will permanently delete the entire database in '{cluster_name}'! If you need the data, please download it before proceeding."
        ):
            click.echo("Deletion aborted.")
            sys.exit(1)
            return  # Exit if the user doesn't confirm

    click.echo(f"------ Deleting cluster {cluster_name} ------")
    has_skipped = run_delete_cluster_commands(cluster_name)
    if not has_skipped:
      click.echo(f"Successfully deleted cluster.")

@cli.command()
@click.option("--repo-url", prompt="Enter the repository URL for the scraper (e.g., https://github.com/your-username/your-repository)", required=True, help="The GitHub repository URL to install.")
@click.option("--name", required=False, help="Optional name for the scraper")
def install_ui_scraper(repo_url, name):
  """Clones and installs a ui scraper from a given GitHub repository"""
  repo_url = repo_url.strip()
  folder_name = name.strip() if name else extractRepositoryName(repo_url)
  click.echo("------------")
  click.echo("Performing the following steps to install the scraper:")
  click.echo("    - Installing Google Chrome")
  click.echo(f"    - Cloning the {folder_name} repository and installing dependencies")
  click.echo("    - Creating systemctl services to ensure the scraper runs continuously on the VM")
  click.echo("------------")
  install_ui_scraper_in_vm(repo_url, folder_name)


# Custom type for max_retry to handle integer >= 0 or 'unlimited'
class MaxRetryParamType(click.ParamType):
    name = "integer>=0 or 'unlimited'"

    def convert(self, value, param, ctx):
        if value == 'unlimited':
            return value
        try:
            int_value = int(value)
            if int_value >= 0:
                return int_value
            else:
                self.fail(
                  f"'{value}' is not valid. Please enter a number greater than or equal to 0, or the word 'unlimited'.",
                  param,
                  ctx,
                )
        except ValueError:
            self.fail(
                f"'{value}' is not a valid integer or the string 'unlimited'.",
                 param,
                 ctx,
            )

# Instantiate the custom type
MAX_RETRY_TYPE = MaxRetryParamType()
@cli.command()
@click.option(
  "--repo-url",
  prompt="Enter the repository URL for the scraper (e.g., https://github.com/your-username/your-repository)",
  required=True,
  help="The GitHub repository URL to install.",
)
@click.option(
  "--max-retry",
  type=MAX_RETRY_TYPE,  # Use the custom type for validation
  required=False,       # Make it optional
  default=3,            # Default to None if not provided
  help="The maximum number of retries for the scraper. Can be a number greater than or equal to 0 or 'unlimited'. Defaults to 3"
)
@click.option(
  "--name",
  required=False,
  help="Optional name for the scraper"
)
def install_scraper(repo_url, max_retry, name):
  """
  Clones and installs a scraper from a given GitHub repository
  """
  repo_url = repo_url.strip()

  folder_name = name.strip() if name else extractRepositoryName(repo_url)
  click.echo("------------")
  click.echo("Performing the following steps to install the scraper:")
  click.echo("    - Installing Google Chrome")
  click.echo(f"    - Cloning the {folder_name} repository and installing dependencies")
  click.echo("    - Creating systemctl service for the scraper")
  click.echo("------------")

  install_scraper_in_vm(repo_url, folder_name, max_retry)

@cli.command()
@click.option(
    "--debian-installer-url",
    prompt="Enter the URL to download the .deb installer",
    required=True,
    type=str,
    help="URL to download the .deb package for the desktop app",
)
@click.option(
    "--port",
    default=8000,
    type=click.IntRange(1, 65535),
    help="Port on which the desktop app will run. Defaults to 8000",
)
@click.option(
    "--skip-apache-request-routing",
    is_flag=True,
    help="Skip setting up Apache request routing",
)
@click.option(
    "--api-base-path",
    default=None,
    type=str,
    help="Specifies the initial URL segment that prefixes all API endpoint paths",
)
def install_desktop_app(debian_installer_url, port, skip_apache_request_routing, api_base_path):
    """
    Installs a desktop app in the VM using the provided .deb installer URL
    """
    # This command will:
    # 1. Download and install the specified .deb package
    # 2. Setup systemctl to run app at all times
    # 3. Optionally configures Apache to route requests

    click.echo("------------")
    click.echo("Performing the following steps to install the desktop app:")
    click.echo(f"    - Downloading and installing the desktop app from {debian_installer_url}")
    click.echo("    - Setting up systemctl to run app at all times")
    if not skip_apache_request_routing:
        click.echo("    - Configuring Apache request routing")
    click.echo("------------")    
    # Call the actual implementation (to be defined elsewhere)
    install_desktop_app_in_vm(
        debian_installer_url.strip(),
        port,
        skip_apache_request_routing,
        api_base_path.strip() if api_base_path else None
    )

@cli.command()
def switch_project():
    """Switches the default project ID"""
    project_id = set_and_get_project_id()
    click.echo(f"Successfully switched to project: {project_id}")

@cli.command()
def switch_region():
    """Switches the default region"""
    region = set_get_region()
    click.echo(f"Successfully switched to region: {region}")


@cli.command()
@click.option("--force", is_flag=True, help="Force deletion of all IP addresses without confirmation. Use this option with caution.")
def delete_all_ips(force):
    """Deletes all IP addresses"""

    project_id = get_project_id()
    region = get_region()  # Get the current region using the get_region function

    ips = list_all_ips_regional(project_id, region)
    if not ips:
        click.echo(f"No IP addresses found in region '{region}'.")
        return

    if not force:
        click.echo(f"The following IP addresses will be deleted in region '{region}':")
        for ip in ips:
            click.echo(f"- {ip}")
        if not click.confirm("Are you sure you want to proceed?"):
            click.echo("Deletion aborted.")
            return

    for ip in ips:
        call_ip = ip.rstrip('-ip')
        if does_ip_exists_regional(call_ip, project_id, region):
            click.echo(f"Deleting IP address '{ip}' ...")
            delete_external_ip_regional(call_ip, project_id, region)
            click.echo(f"IP address '{ip}' deleted successfully.")
        else:
            click.echo(f"IP address '{ip}' not found or already deleted.")

    click.echo(f"Successfully deleted all IP addresses in region '{region}'.")


@cli.command()
def list_all_ips():
    """Lists all IP addresses"""

    project_id = get_project_id()
    region = get_region()  # Get the current region using the get_region function

    ips = list_all_ips_regional(project_id, region)
    if not ips:
        click.echo(f"No IP addresses found in region '{region}'.")
        return

    click.echo(f"You have following IP addresses in region '{region}':")
    for ip in ips:
        click.echo(f"- {ip}")

# python -m src.bota.__main__
if __name__ == "__main__":
    cli()
    # Usage examples:
    # 1. python -m botasaurus_server build --cluster-name omkar --workers 1 --use-browser true
    # 2. python -m botasaurus_server create-cluster --cluster-name omkar --nodes 1
    # 3. python -m botasaurus_server delete-cluster --cluster-name omkar --force
