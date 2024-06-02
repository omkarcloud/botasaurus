### How to Run the Scraper in Kubernetes?

Let's learn how to run your scraper in a Kubernetes cluster with Continuous Deployment (CD) using GitHub Actions.

With GitHub Actions, whenever you push your code to GitHub, the scraper will be automatically deployed to the Kubernetes cluster with the latest changes.

To achieve this, we will:
1. Create a Kubernetes cluster in Google Cloud
2. Create a GitHub repository
3. Add deployment secrets like Google Cloud access keys to the GitHub repository
4. Run the GitHub Workflow to deploy the scraper

### Step 1: Create the Kubernetes Cluster

1. If you don't have a Google Cloud account, create one. You'll receive a $300 credit to use over 3 months.
   ![Select-your-billing-country](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/Select-your-billing-country.png)

2. Visit the [Google Cloud Console](https://console.cloud.google.com/welcome?cloudshell=true) and click the Cloud Shell button. A terminal will open up.
   ![click-cloud-shell-btn](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/click-cloud-shell-btn.png)

3. Run the following commands in the terminal to create the Kubernetes cluster:

   ```bash
   python -m pip install bota
   python -m bota create-cluster
   ```

   You will be prompted for the following information:

   > name: Enter a cluster name of your choice, for example, "pikachu".

   > machine: Press Enter to accept the default machine type, which is "us-central1".

   > number of machines: Press Enter to accept the default number of machines, which is 2.

   > region: Press Enter to accept the default region, which is "us-central1". (This is asked the first time only)

   ![Install bota cluster](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/install-bota-cluster.gif)

   After the command completes, note the IP of the Kubernetes Cluster, as we will later visit this IP to use the scraper.
   ![k8 ip](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/k8-ip.png)

### Step 2: Create a GitHub Repository

1. Clone the Botasaurus starter template to your machine by running the following commands:
   ```bash
   git clone https://github.com/omkarcloud/botasaurus-starter kubernetes-scraper
   cd kubernetes-scraper
   code .
   ```
2. Create Github Actions Workflow YAML and Kubernetes deployment YAML files by running the following command:

   ```bash
   python -m bota create-manifests
   ```

You will be prompted for the following information:

> Enter cluster name: Enter the exact same name you used earlier for the cluster (e.g., pikachu).

> number of workers to run: Press Enter to accept the default number of workers, which is 1.

> Are browsers used in the scraper: Enter "Yes" if the scraper uses a browser, as this will increase the CPU and RAM allocation for the scraper because browser-based scrapers need more resources. Since the Botasaurus Starter Templates do not use a browser, enter "No".

> region: Enter the exact same region you used earlier in the Google Cloud Shell (e.g., us-central1). (This is asked the first time only)
   ![create manifests](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/create-manifests.png)

3. Next, Create a new private repository on GitHub named `kubernetes-scraper`.
   ![create repository](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/create-repository.png)

4. In your local machine, run the following commands to push the code to GitHub, remember to replace `USERNAME` with your GitHub username:

   ```bash
   rm -rf .git # remove the existing git repository
   git init
   git add .
   git commit -m "Initial Commit"
   git remote add origin https://github.com/USERNAME/kubernetes-scraper # TODO: replace USERNAME with your GitHub username
   git branch -M main
   git push -u origin main
   ```

### Step 3: Add Deployment Secrets to the GitHub Repository
1. Visit [this link](https://console.cloud.google.com/iam-admin/serviceaccounts) and click the "CREATE SERVICE ACCOUNT" button.
   ![create sa](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/create-sa.png)

2. Enter a name like "Owner" in the "Service account name" textbox and click the "CREATE AND CONTINUE" button.
   ![create name](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/create-name.png)

3. Click on the "Select a role" dropdown, select "Project" > "Owner" role, and click the "CONTINUE" button.
   ![select role](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/select-role.png)

4. Click on the "DONE" button.
   ![create key](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/create-key.png)

5. Download the JSON key for the service account by following the GIF below.
   ![download key](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/download-key.gif)

6. Go to [base64encode.org](https://www.base64encode.org/), paste the service account key's JSON contents, and encode it to base64.
   ![encode sa](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/encode-sa.gif)

7. Go to the GitHub repository you just created, click on "Settings" > "Secrets and variables" > "Actions", and click on the "New repository secret" button.
   ![secrets](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/secrets.png)

8. Enter "GKE_KEY" as the name and paste the base64-encoded GKE_KEY as the value. Then click the "Add secret" button.
   ![add gke sa](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/add-gke-sa.png)

9. Add a new secret with the name "GKE_PROJECT" and enter the project ID (found in the service account's 'project_id' field) as the value.
   ![add gke project](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/add-gke-project.png)

### Step 4: Run the GitHub Workflow to Deploy the Scraper

1. Go to the "Actions" tab in your GitHub repository, click on the workflow tab, and re-run the workflow.
   ![rerun workflow](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/rerun-workflow.gif)

2. That's it, Once the workflow is completed, visit the IP you copied earlier to use the scraper.
   ![k8-final](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/k8-final.png)

## How to delete the scraper and avoid incurring charges?

If you are deleting a custom scraper you deployed, ensure you have downloaded the results from it.

Next, in the Cloud Shell, run the following command to delete the Kubernetes scraper:
```bash
python -m bota delete-cluster
```

When prompted for cluster name, enter the exact same cluster name you used earlier (e.g., "pikachu").
![delete k8](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/delete-k8.gif)

That's it! You have successfully deleted the Kubernetes cluster and all associated resources. You will not incur any further charges.