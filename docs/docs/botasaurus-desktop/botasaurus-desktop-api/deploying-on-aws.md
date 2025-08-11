---
sidebar_position: 31
---

# Deploying on AWS EC2

This guide will help you deploy your Botasaurus Desktop API on an AWS EC2 instance. The process is straightforward and involves creating an Elastic IP, setting up an EC2 instance, and installing your desktop application.

### Step-by-Step Deployment Guide

### 1. Reserve a Static IP Address

First, we'll reserve an Elastic IP address. An Elastic IP ensures your EC2 instance is always reachable at the same IP address.

1. Create an [AWS Account](https://signin.aws.amazon.com/signup?request_type=register) if you don't already have one.
   ![AWS-signup](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/aws-signup.png)

2. Go to the [Elastic IP addresses](https://console.aws.amazon.com/ec2/home?#Addresses:) page.
   ![Elastic IP addresses page](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/aws-elastic-ip-addresses-page.png)

3. Click the "Allocate Elastic IP address" button.
   ![Allocate Elastic IP address button](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/aws-allocate-elastic-ip-address-button.png)

4. Keep the default settings and click "Allocate"
   ![Allocate Elastic IP address dialog](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/aws-allocate-elastic-ip-address-dialog.png)

This creates an Elastic IP address that you'll use to access your app. You will assign this IP to your EC2 instance in the next step.

   
### 2. Create an AWS EC2 Instance

1. Go to the [EC2 Dashboard](https://console.aws.amazon.com/ec2/v2/home#Instances:) and click "Launch Instance"
![Launch Instance button](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/aws-launch-instance-button.png)

2. Configure your instance with these recommended settings. You may change the Machine Type and Boot Disk Size based on your scraping needs:

| Section | Setting | Value | Notes |
|---------|---------|-------|-------|
| Name and tags | Name | yahoo-finance | Use your app name as the instance name |
| Application and OS Images (AMI) | Amazon Machine Image (AMI) | Ubuntu Server 24.04 LTS | A `.deb` installer requires a Debian-based OS like Ubuntu. |
| Instance type | Instance type | t3.medium | 2 vCPU, 4 GB memory. Change based on needs |
| Key pair (login) | Key pair name | Create new key pair > RSA (.pem) | Required for SSH access |
| Network settings | Allow SSH traffic from | ✓ | Required for terminal access |
| Network settings | Allow HTTP traffic from the internet | ✓ | Required for accessing API via HTTP |
| Network settings | Allow HTTPS traffic from the internet | ✓ | Required for accessing API via HTTPS |
| Configure storage | Storage | 20 GiB - Magnetic | **Magnetic** is the cheapest disk type. |

    ![deploy-vm](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/deploy-vm-ec2.gif)

3. Optionally, if you're scraping data for your own needs, enable Spot Instances as they are 70-90% cheaper than On-Demand instances. Enable them with these settings:

| Section | Setting | Value | Notes |
|---------|---------|-------|-------|
| Advanced details | Purchasing option | Spot Instances | Enables Spot Instances |
| Customize Spot instance options | Request type | Persistent | - |
| Customize Spot instance options | Interruption behavior | Stop | - |

:::warning
Don't use Spot VMs for customer-facing APIs or mission-critical applications, as they can be stopped by AWS at any time if the resources are needed elsewhere.
:::

4. Click **Launch instance**.

5. Now, associate the Elastic IP:
   - Go to [Elastic IPs](https://console.aws.amazon.com/ec2/v2/home#Addresses:)
   - Select your previously created Elastic IP
   - Click **Actions** > **Associate Elastic IP address**
   - Select your newly created instance and click **Associate**

   ![Associate Elastic IP](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/aws-associate-elastic-ip.gif)

6. Connect to your instance via SSH:
   - Go to [EC2 Instances](https://console.aws.amazon.com/ec2/v2/home#Instances:)
   - Select your instance
   - Click **Connect** > **EC2 Instance Connect**
   - Click the **Connect** button

   ![AWS SSH Connect](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/aws-ssh-connect.gif)


### 3. Installing Your Desktop App

Now that your EC2 instance is ready, let's install your Botasaurus Desktop API.

1. First, install the necessary packages on your instance by running the command below. This script installs Botasaurus CLI and the Apache web server to manage requests to your app.

   ```bash
   curl -sL https://raw.githubusercontent.com/omkarcloud/botasaurus/master/vm-scripts/install-bota-desktop.sh | bash
   ```
   ![Install scraper](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/install-packages-ec2.gif)

2. Upload your app to S3 following the [packaging and publishing guide](../packaging-publishing.md). A Debian installer will be saved in the S3 bucket, which we will use in the next step. It looks like this: 

   ```bash 
   https://your-bucket.s3.amazonaws.com/Your-App-amd64.deb
   ```

3. Next, install the desktop application on the EC2 instance.

   - If you have already uploaded your app to S3, replace the link in the command below with your own Debian installer URL.
   - If you only want to test the installation, keep the sample URL as is.

   ```bash
   python3 -m bota install-desktop-app --debian-installer-url https://yahoo-finance-extractor.s3.us-east-1.amazonaws.com/Yahoo+Finance+Extractor-amd64.deb
   ```

   ![Install scraper](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/install-desktop-scraper-ec2.gif)

   :::info[Configuration Options]
    The `install-desktop-app` command supports these options:
    - `--port`: Sets the port for the app (e.g., `8001`). An alternative to `ApiConfig.setApiPort`.
    - `--api-base-path`: Adds a prefix to all API routes (e.g., `/yahoo-finance`). An alternative to `ApiConfig.setApiBasePath`.
    - `--skip-apache-request-routing`: Disables automatic Apache configuration for the API. Use it if you want to manually configure other load balancers like Nginx.
   :::

When the installation completes, you'll see a **link** to your API documentation. Visit it see the api.

![vm-success](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/vm-success-ec2.png)

:::tip[Hosting Multiple Desktop APIs on One EC2 Instance]
To host additional applications on the same instance, you must use the `--port` and `--api-base-path` flags to prevent conflicts:
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
The Amazon Invoice API will now be available at: `http://<your-elastic-ip>/amazon-invoices`.
:::

### How to Uninstall the Desktop App?
:::warning[Backup Your Data]
Before uninstalling, download any important data. This action is irreversible and will result in permanent data loss.
:::

To uninstall the application from the EC2 instance, use one of the following methods:

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
### How to Delete the EC2 Instance and Avoid Incurring Further Charges?

:::warning[Backup Your Data]
Before deleting the instance, download any important data to avoid permanent loss.
:::

To prevent ongoing costs, you must delete both the EC2 instance and release the Elastic IP address as follows:

1. **Cancel the Spot Request** *(Spot VMs only)*
   If you have enabled Spot Instances, cancel the Spot request before deleting the instance. Otherwise, they will keep respawning, again and again. To cancel the Spot request:

   - Go to [Spot Requests](https://console.aws.amazon.com/ec2/v2/home#SpotInstances:)
   - Select your Spot request
   - Click **Actions** > **Cancel request**
   - Click **Confirm** to cancel

   ![Cancel Spot Request](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/cancel-spot-request-ec2.gif)

2. **Terminate the EC2 Instance**

   - Go to [EC2 Instances](https://console.aws.amazon.com/ec2/v2/home#Instances:)
   - Select your instance
   - Click **Instance state** > **Terminate (delete) instance**
   - Click **Terminate (delete)** to confirm

   ![Delete VM](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/delete-vm-ec2.gif)

3. **Release the Elastic IP Address**

   - Go to [Elastic IPs](https://console.aws.amazon.com/ec2/v2/home#Addresses:)
   - Select your Elastic IP
   - Click **Actions** > **Release Elastic IP address**
   - Click **Release** to confirm

   ![Delete IP](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/aws/delete-ip-ec2.gif)

That's it! You have successfully deleted the EC2 instance and released the Elastic IP. You will not incur any further charges.