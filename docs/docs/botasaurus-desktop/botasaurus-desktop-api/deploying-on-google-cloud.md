---
sidebar_position: 30
---
# Deploying on Google Cloud VM

Deploying your API on Cloud VM allows you to:
- Run your scrapers 24/7
- Access your scrapers from anywhere via HTTP Endpoints
- Scale to multiple instances based on your scraping needs

This guide walks you through deploying your **Botasaurus Desktop API** on a Google Cloud VM instance.

### Prerequisites

This guide uses **Google Cloud VM**, but the steps apply to any cloud provider (AWS, Azure, DigitalOcean, etc.) as long as the VM runs a Debian or Ubuntu-based OS.

### Step-by-Step Deployment Guide

### 1. Reserve a Static IP Address

First, we'll reserve a static IP address. A static IP ensures your VM is always reachable at the same IP address.

1. Create a Google Cloud Account if you don't already have one.
   ![Select-your-billing-country](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/Select-your-billing-country.png)

2. Visit the [Google Cloud Console](https://console.cloud.google.com/welcome?cloudshell=true) and click the Cloud Shell button. A terminal will open up.
   ![click-cloud-shell-btn](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/click-cloud-shell-btn.png)

3. Install the Botasaurus CLI and create a static IP address by running the following commands:

   ```bash
   python -m pip install bota --upgrade 
   python -m bota create-ip # Create a static IP address for your VM
   ```

   The CLI will prompt you for a name for your VM. Use a relevant name like your app name, such as `yahoo-finance`.

   > Name: yahoo-finance

   Next, it will ask for a region. Press **Enter** to accept the default (`us-central1`), which offers the lowest-cost VMs. 

   > Region: Default

   ![Install bota](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/install-bota.gif)

   This creates a static IP address that you'll use to access your app. You will assign this IP to your VM in the next step.
   
### 2. Create a Google Cloud VM

1. Go to [VM Instances](https://console.cloud.google.com/compute/instances) and create a VM with these specifications. You may change the Machine Type and Boot Disk Size based on your scraping needs:

   | Section | Setting | Value | Notes |
   |---------|---------|-------|-------|
   | Machine configuration | Name | yahoo-finance | Use your app name as the instance name |
   | Machine configuration | Region | us-central1 | **Must match** the region you selected for the static IP. |
   | Machine configuration | Zone | Any | Leave it any zone within selected region |
   | Machine configuration | Series | E2 | Cost-effective choice |
   | Machine configuration | Machine Type | e2-medium | 2 vCPU, 4 GB memory. Change based on your needs |
   | OS and storage | Boot Disk Type | Standard persistent disk | Cheapest disk, suitable for scraping |
   | OS and storage | Boot Disk Size | 20 GB | Change based on your storage needs |
   | Data protection | Back up your data | No backups | No backups needed for scraping, as the data can be easily regenerated. |
   | Networking | Firewall/Allow HTTP traffic | ✓ | Required for accessing API via HTTP |
   | Networking | Firewall/Allow HTTPS traffic | ✓ | Required for accessing API via HTTPS |
   | Networking | Firewall/Allow Load Balancer Health Checks | ✓ | - |
   | Networking | Network Interfaces/External IPv4 address | yahoo-finance-ip | Select the static IP you created in the previous step. |
   | Observability | Ops Agent | Uncheck Install Ops Agent for Monitoring and Logging | Helps reduce logging costs |

    ![deploy-vm](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/deploy-vm-gcp.gif)

2. Optionally, if you're scraping data for your own needs, enable Spot VMs as they are 60-91% cheaper than standard VMs. Enable them by going to **Advanced** > **Provisioning model** and selecting **Spot**.

   ![spot vm](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/spot-vm.png)

   :::warning
   Don't use Spot VMs for customer-facing APIs or mission-critical applications, as they can be stopped by Google at any time if the resources are needed elsewhere.
   :::

3. Click the **Create** button. The VM will be provisioned in a few minutes.
   ![Create VM](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/create-vm.png)


4. Once the VM is running, connect to it by clicking the **SSH** button on the [VM Instances page](https://console.cloud.google.com/compute/instances).
   ![ssh-vm](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/ssh-vm.png)

### 3. Installing Your Desktop App

Now that your VM is ready, let's install your Botasaurus Desktop API.

1. First, install the necessary packages on your VM by running the command below. This script installs Botasaurus CLI and the Apache web server to manage requests to your app.

   ```bash
   curl -sL https://raw.githubusercontent.com/omkarcloud/botasaurus/master/vm-scripts/install-bota-desktop.sh | bash
   ```
   ![Install scraper](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/install-packages-gcp.gif)

2. Upload your app to S3 following the [packaging and publishing guide](../packaging-publishing.md). A Debian installer will be saved in the S3 bucket, which we will use in the next step. It looks like this: 

   ```bash 
   https://your-bucket.s3.amazonaws.com/Your-App-amd64.deb
   ```


3. Next, install the desktop application on the VM.

   - If you have already uploaded your app to S3, replace the link in the command below with your own Debian installer URL.
   - If you only want to test the installation, keep the sample URL as is.

   ```bash
   python3 -m bota install-desktop-app --debian-installer-url https://yahoo-finance-extractor.s3.us-east-1.amazonaws.com/Yahoo+Finance+Extractor-amd64.deb
   ```

   ![Install scraper](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/install-desktop-scraper.gif)

   :::info[Configuration Options]
    The `install-desktop-app` command supports these options:
    - `--port`: Sets the port for the app (e.g., `8001`). An alternative to `ApiConfig.setApiPort`.
    - `--api-base-path`: Adds a prefix to all API routes (e.g., `/yahoo-finance`). An alternative to `ApiConfig.setApiBasePath`.
    - `--skip-apache-request-routing`: Disables automatic Apache configuration for the API. Use it if you want to manually configure other load balancers like Nginx.
   :::

When the installation completes, you'll see a **link** to your API documentation. Visit it see the api.

![vm-success](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/vm-success-gcp.png) highlight


:::tip[Hosting Multiple Desktop APIs on One VM]
To host additional applications on the same VM, you must use the `--port` and `--api-base-path` flags to prevent conflicts:
- `--port` with different ports (e.g., `--port 8001`)
- `--api-base-path` with unique paths (e.g., `--api-base-path /amazon-invoices`)

For example, run this command to add an Amazon Invoice extractor alongside the Yahoo Finance extractor:
```sh
python3 -m bota install-desktop-app \
  --debian-installer-url https://amazon-invoice-extractor.s3.us-east-1.amazonaws.com/Amazon+Invoice+Extractor-amd64.deb \
  // highlight-next-line
  --port 8001 \
  // highlight-next-line
  --api-base-path /amazon-invoices
```
The Amazon Invoice API will now be available at: `http://<your-vm-ip>/amazon-invoices`.
:::

### How to Uninstall the Desktop App?

:::warning[Backup Your Data]
Before uninstalling, download any important data. This action is irreversible and will result in permanent data loss.
:::

To uninstall the application from the VM, use one of the following methods:


**Method 1: Using Debian Installer URL**

Replace `https://yahoo-finance-extractor.s3.us-east-1.amazonaws.com/Yahoo+Finance+Extractor-amd64.deb` with your app's Debian installer URL:

```bash 
python3 -m bota uninstall-desktop-app --debian-installer-url https://yahoo-finance-extractor.s3.us-east-1.amazonaws.com/Yahoo+Finance+Extractor-amd64.deb
```


**Method 2: Using Package Name**

1. Find your package **name** in `package.json`:
   ![Example of package.json file](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/package-json-example.png)

2. Uninstall using the package **name**:
   ```bash
   python3 -m bota uninstall-desktop-app --package-name yahoo-finance-extractor
   ```

### How to Delete the VM and Avoid Incurring Further Charges?

:::warning[Backup Your Data]
Before deleting VM, download any important data to avoid permanent loss.
:::

To prevent ongoing costs, you must delete both the VM instance and its static IP address as follows:

1. Delete the static IP by running the following command:

   ```bash
   python -m bota delete-ip
   ```

   The CLI will prompt you for the name of the VM you created in the first step. Enter the name and press Enter.

   ![Delete IP](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/delete-ip.png)

2. Go to [VM Instances](https://console.cloud.google.com/compute/instances) and delete your VM.

   ![Delete VM](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/delete-compute-vm.png)

That's it! You have successfully deleted the VM and the IP. You will not incur any further charges.


### How to Reduce Compute Costs?


Running VMs is expensive, but there are a few decent ways to reduce costs:

- Choose the right machine type. Avoid overprovisioning CPU and memory. Start with a smaller instance like `e2-medium` for browser-based scrapers and `e2-small` for requests/task-based scrapers.

   Then, check the CPU and memory usage on the VM Instance Observability Page.

   ![Example of VM Instance Observability Page](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/vm-instance-observability-page.png)

   If you find your VM's CPU and memory are underutilized, you can downgrade to a smaller machine type. If they're overutilized, you can upgrade to a larger machine type.

- Use Spot VMs for personal/non-critical workloads. Spot VMs are up to 60-91% cheaper than standard VMs, but they can be stopped by Google at any time if the resources are needed elsewhere.

   The Botasaurus task management system is fault-tolerant, making it well-suited for Spot VMs.

   **Spot VMs are perfect for:**
   - Personal scraping
   - Batch jobs where you can check the results later

   **Avoid Spot VMs when:**
   - Running customer-facing APIs that require high availability
   - Running mission-critical applications that cannot tolerate downtime

   To use a Spot VM, when creating VM, go to **Advanced** > **Provisioning model** and select **Spot**.

   ![spot vm](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/spot-vm.png)

- If you have a stable, long-term workload, you can achieve significant savings by committing to 1-year (37% discount) or 3-year terms (55-70% discount).


      :::tip CUDs: Pros and Cons
      **Pro:** Significant discounts for predictable workloads.
      **Con:** You are locked into paying for the committed resources for the entire term, even if you stop using the VM. We recommend running a VM with on-demand pricing for 2 months to confirm your needs before committing.
      :::


### Should I Choose On-Demand, 1-Year CUD, or 3-Year CUD?

Excellent question. Choosing the right GCP pricing model can save you thousands of dollars in compute costs, so read this carefully.

Let's simplify the decision by calculating the "break-even" point—the moment when a longer commitment becomes the cheaper option.

#### Step 1: Find Your Monthly Costs

First, you need the numbers. Go to the [GCP Pricing Calculator](https://cloud.google.com/products/calculator?dl=CjhDaVEyWVRGa1lqVmlOeTFtTXpsakxUUXpOVGd0T1dNM1ppMDBaRGcyWm1NelkyTXlaVE1RQVE9PRAIGiQyOEQ1QjQwNi05RjNGLTRBNkQtODczMS0wNTYzQzQ4QjgxRUU) and find the monthly costs for your machine type across all three pricing models.

![GCP Pricing Calculator](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/gcp-pricing-calculator.png)

For this example, we'll use an **e2-medium** instance with a **20GB Standard Persistent Disk**:
-   **On-Demand Price:** $24.46/month
-   **1-Year CUD Price:** $15.41/month
-   **3-Year CUD Price:** $11.01/month

#### Step 2: Calculate the Break-Even Points

With these prices, we can answer two key questions by setting up simple equations.

#### When does a 1-Year CUD beat On-Demand pricing?

When you choose a CUD, you're committed to paying for the full term, regardless of usage. The break-even point is the number of months it would take for your on-demand spending to equal the total fixed cost of the 1-year commitment.

-   **Total cost of a 1-Year Commitment:** 12 months × $15.41/month = **$184.92**

Let's find the break-even point in months (X):
-   `X months × On-Demand Price = Total 1-Year Cost`
-   `X × $24.46 = $184.92`
-   `X = $184.92 / $24.46`
-   `X = 7.5 months`

**Conclusion:** If you expect to need the virtual machine for **8 months or more**, the 1-Year CUD is the wise choice.

#### When does a 3-Year CUD beat consecutive 1-Year CUDs?

This is the most important decision for long-term projects. We want to find when locking in for 3 years becomes more profitable than renewing 1-year CUD commitments.

-   **Total cost of a 3-Year Commitment:** 36 months × $11.01/month = **$396.36**

Let's find how many months (X) of the 1-year plan this total 3-year cost would cover:
-   `X months × 1-Year CUD Price = Total 3-Year Cost`
-   `X × $15.41 = $396.36`
-   `X = $396.36 / $15.41`
-   `X = 25.7 months`

**Conclusion:** The financial break-even point is approximately **2 years and 2 months**. If you're confident your resource will be needed for 26 months or longer, the 3-Year CUD is the more financially sound choice from day one.

#### Step 3: Ask the Critical Question

Now, look at your project and your business, then ask one simple question:

**"How long will my app need to be online?"**

#### Step 4: Choose Your Scenario

Based on your answer, choose the most appropriate pricing model:

-   **Choose On-Demand Pricing if:** You're just starting out, have no customers, or expect the server to run for **less than 8 months**. This offers maximum flexibility with no commitment.

-   **Choose a 1-Year CUD if:** You expect your app to run for **at least 8 months but are unsure about a 2+year timeframe**. This provides significant savings over on-demand pricing without a multi-year lock-in. Recommended scenarios include:
      - A new B2B service with 10-50 paying customers

-   **Choose a 3-Year CUD if:** You're confident your application will run for **at least 2 years and 2 months**. This is the best choice for stable, long-term workloads. Recommended scenarios include:
      - A business website that you're sure will be online for the foreseeable future (e.g., for omkar.cloud, I chose a 3-year CUD)
      - A popular scraping API with 100+ paying customers

#### Summary Table

| Plan | Best For | Risk | Savings |
|------|----------|------|---------|
| **On-Demand** | < 8 months usage, uncertain projects | None | 0% |
| **1-Year CUD** | 8-26 months usage, moderate certainty | Low | ~37% |
| **3-Year CUD** | 26+ months usage, high certainty | Medium | ~55% |

#### Break-Even Table

Here's a table showing the approximate break-even months for different E2 machine types (with a 20GB persistent disk). Note that the break even months are the same across all E2 types:

| Machine Type | Break-even: On-Demand vs 1-Year CUD | Break-even: 1-Year CUD vs 3-Year CUD |
|:---|:---:|:---:|
| **e2-small** | ~8 months (7.5) | ~2 years, 2 months (25.7) |
| **e2-medium** | ~8 months (7.5) | ~2 years, 2 months (25.7) |
| **e2-standard-2** | ~8 months (7.5) | ~2 years, 2 months (25.7) |

#### How to Calculate for Any Machine Type

For any other machine type, simply plug the prices from the GCP Pricing Calculator into these formulas:

**Break-even months for On-Demand vs 1-Year CUD:**
```
= (1-Year CUD Monthly Cost × 12) / On-Demand Monthly Cost
```

**Break-even months for 1-Year CUD vs 3-Year CUD:**
```
= (3-Year CUD Monthly Cost × 36) / 1-Year CUD Monthly Cost
```

Maths is awesome, isn't it? Use this knowledge to choose the right CUDs, and save significant money on compute costs.

### How to Apply Committed Use Discounts?

#### Step 1: Find your CUD Requirements

Before purchasing CUDs, carefully analyze your resource needs:

1. Monitor your VM's Observability Page for at least 1 month to identify underutilized resources. If your VM consistently uses less than 50% of its RAM/CPU, consider downgrading to a smaller machine type first.
   
   ![Example of VM Instance Observability Page](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/vm-instance-observability-page.png)

2. Visit the [CUD Analysis Page](https://console.cloud.google.com/billing/commitments/analysis) to see your current memory and vCPU usage. 

   ![GCP CUD Recommendations](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/gcp-cud-recommendations.gif)

3. Next, find your instance's vCPU count using the [Pricing Calculator](https://cloud.google.com/products/calculator?hl=en&dl=CjhDaVF5WldVMFlUZzNPUzFqTm1Ka0xUUTBOelF0WVRBM1pDMW1NREE1TURNNVltTTBaRE1RQVE9PRAIGiRFNUZGNEQ3OC1EMTdELTRGMDktOUMzOC00NUIyNDhDOTU1MTU).

   ![Example of vCPU count in Pricing Calculator](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/calc-vcpu-count.png)

   For quick reference, here are the vCPU counts for common E2 machine types:

   | Machine Type | vCPUs |
   |--------------|-------|
   | e2-micro     | 0.25  |
   | e2-small     | 0.5   |
   | e2-medium    | 1     |
   | e2-standard-2| 2     |
   | e2-standard-4| 4     |

   :::warning[Use Pricing Calculator vCPU Values]
   The vCPU count displayed when creating an instance is incorrect:

   ![Example of vCPU count in Create Page](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/gcp-cud-create.png)

   **Always** use the vCPU count from the [Pricing Calculator](https://cloud.google.com/products/calculator?hl=en&dl=CjhDaVF5WldVMFlUZzNPUzFqTm1Ka0xUUTBOelF0WVRBM1pDMW1NREE1TURNNVltTTBaRE1RQVE9PRAIGiRFNUZGNEQ3OC1EMTdELTRGMDktOUMzOC00NUIyNDhDOTU1MTU) when purchasing CUDs:

   ![Example of vCPU count in Pricing Calculator](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/calc-vcpu-count.png)
   :::
4. Next, find your instance's memory size in GB using the same [Pricing Calculator](https://cloud.google.com/products/calculator?hl=en&dl=CjhDaVF5WldVMFlUZzNPUzFqTm1Ka0xUUTBOelF0WVRBM1pDMW1NREE1TURNNVltTTBaRE1RQVE9PRAIGiRFNUZGNEQ3OC1EMTdELTRGMDktOUMzOC00NUIyNDhDOTU1MTU).

5. Calculate your total resource needs by multiplying the per-instance resources by the number of instances you plan to run.

   For example, if you need 2 `e2-medium` instances (1 vCPU, 4GB memory each):
   - **Total Memory Needed:** 2 × 4 GB = 8 GB
   - **Total vCPUs Needed:** 2 × 1 vCPU = 2 vCPUs

6. Finally, choose your commitment duration:
   - **1 Year** – Ideal for workloads running at least 8 months
   - **3 Years** – Ideal for long-term projects running over 2 years and 2 months

7. CUDs are non-refundable commitments. So, take **at least 2 days** to consider:
   - Have you right-sized your instances?
   - Is the commitment duration right for your project?
   - Will your resource needs change during the commitment period?

   There's a good chance you might reconsider the **commitment duration** or **instance types** after **2 days**.

   **Don't skip** this step — it's a crucial pause that could save you from a costly mistake.

#### Step 2: Create Your CUDs

1. Go to the [Compute Commitments page](https://console.cloud.google.com/compute/commitments).

   ![Commitments Page](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/commitments-page.png)

2. Click **Purchase Commitments**.

   ![Purchase Commitments](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/purchase-commitments.png)

3. Create a memory CUD with these settings:

   | Field | Value |
   |-------|-------|
   | Name | your-app-memory-cud (use a descriptive name) |
   | Region | us-central1 (must match your VM's region) |
   | Commitment Type | General-purpose E2 (must match your VM series) |
   | Duration | 1 year or 3 years |
   | Memory | Total GB calculated in Step 1 |
   | Reservations | Don't attach reservations |

   ![Create Memory CUD](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/create-memory-cud.png)

4. Create a vCPU CUD with these settings:

   | Field | Value |
   |-------|-------|
   | Name | your-app-vcpu-cud (use a descriptive name) |
   | Region | us-central1 (must match your VM's region) |
   | Commitment Type | General-purpose E2 (must match your VM series) |
   | Duration | 1 year or 3 years |
   | vCPUs | Total vCPUs calculated in Step 1 |
   | Reservations | Don't attach reservations |

   ![Create vCPU CUD](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/create-vcpu-cud.png)

After creation, both CUDs will appear on the [Commitments page](https://console.cloud.google.com/compute/commitments):

<!-- TODO:MAKE -->
![Commitments Page](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/commitments-with-cud-page.png)

You can see your CUD utilization and savings on the [CUD Analysis Page](https://console.cloud.google.com/billing/commitments/analysis).

### When creating a CUD, I get "The COMMITMENTS-per-project-region quota maximum in region us-central1 has been exceeded." error. How do I fix it?

If you encounter an error like **Creating commitment "commitment-20250727-141128" failed. Error: The COMMITMENTS-per-project-region quota maximum in region us-central1 has been exceeded.**:
![Error Message](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/cud-error.png)

This occurs because your maximum number of CUDs allowed in a region is 0. To resolve this:

1. Visit the [Quotas page](https://console.cloud.google.com/iam-admin/quotas) and in search enter **commitments**.
![Quotas page](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/quotas-page.png)

2. Scroll down to your region (e.g., 6us-central1`) and click the **Edit Quotas** button.
![Edit Quotas](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/edit-quotas.png)

3. Enter a higher quota, such as **6**. 

4. For **Request Description**, enter:

```
We have reached the commitment quota limit in us-central1. An increase is required to purchase a new commitment for a production workload.
```

![Request Description](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/request-description.png)

5. Click **Next**, then **Submit Request**.

![Submit Request](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/submit-request.png)

6. Within a minute, you'll receive a confirmation email. Wait ~15 minutes more, and then you will be able to create the CUD.
![Quota Increase Confirmation Email](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/gcp/quota-increase-confirmation-email.png)

### Can I apply Committed-Use Discounts (CUDs) to Spot VMs?
No—**Committed Use Discounts (CUDs)** apply only to standard VMs. Spot VMs are charged separately.

If you have an active CUD and also run Spot VMs, you will essentially be billed twice:
1. For the Spot VM usage at its current (low) price
2. For the resources you committed to via the CUD, whether you use them or not

Therefore, do not mix Spot VMs with CUDs for the same resource types.
