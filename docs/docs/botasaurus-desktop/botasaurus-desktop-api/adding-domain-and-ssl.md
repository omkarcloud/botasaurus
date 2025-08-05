---
sidebar_position: 50
---

# Adding a Domain Name and SSL

This guide shows you how to:

1. Point a domain name to the VM that hosts your Botasaurus Desktop API.
2. Secure that domain with a free SSL certificate from [Let's Encrypt](https://letsencrypt.org/).

## Why Use a Custom Domain?

A custom domain with SSL provides two key benefits:

- **Professional appearance**: `api.yourcompany.com` looks more professional than an IP address
- **Trust**: HTTPS encryption builds trust and prevents browser security warnings

### When to Use a Custom Domain?

**You DON'T need a domain if:**
- You're using the API for personal scripts or automation
- You're listing your API on marketplaces like RapidAPI, which provides its own domain and SSL

**You DO need a domain if:**
- You're providing API access to customers
- You want a professional, branded endpoint


## How to Add a Domain Name and SSL?

The process involves two main steps:

- Pointing your domain to the VM's IP address
- Installing a free SSL certificate



### Step 1: Get a Domain and Point it to Your VM


1. If you don't already have a domain, purchase one from a registrar.

   I recommend these registrars:

   - **Cloudflare Domains** - Cheapest option (offers at-cost pricing, charging only the  ICANN registry fees with no markup)
   - **Porkbun** - Second cheapest option
   - **Namecheap**

   Avoid GoDaddy. While their initial registration costs are low, renewal prices are significantly higher than Porkbun and Namecheap, costing more in the long run.

   I personally use Porkbun because it offers auto-renewals and sends multiple renewal reminders (45 days and 30 days before expiry), so I don't forget to renew my domains.

   ![Porkbun Renewal Emails](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/domains/porkbun-renewal-emails.png)

   Also, Porkbun's logo and branding are funny, nevertheless they provide a good experience and are [highly ratings on Trustpilot.](https://www.trustpilot.com/review/porkbun.com)

2. Next, log in to your domain registrar and create DNS **A records** pointing to your VM's IP address.

    - To host on a root domain and `www` subdomain (e.g., `yahoo-finance.com` and `www.yahoo-finance.com`):

    | Type | Host | Value |
    |------|------|-------|
    | A    | w&#8203;ww.yahoo-finance.com | YOUR_VM_EXTERNAL_IP |
    | A    | yahoo-finance.com | YOUR_VM_EXTERNAL_IP |

    - To host on a subdomain like `yahoo-finance.john-doe-it-solutions.com` (allows hosting multiple scrapers on a single domain):

    | Type | Host | Value |
    |------|------|-------|
    | A    | yahoo-finance.john-doe-it-solutions.com | YOUR_VM_EXTERNAL_IP |

    Here's an example DNS configuration in Porkbun:
    ![Porkbun DNS A Record Example](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/domains/porkbun-dns-a-record.png)

After a few minutes, test your domain by accessing it via HTTP:
![Example of accessing app using domain name](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/domains/accessing-app-using-domain-name.png)

### Step 2: Install SSL Certificate

Next, we'll use **Certbot** from [Let's Encrypt](https://letsencrypt.org/) to automatically issue and install a free SSL certificate.

1. SSH into your VM instance.
![Example of SSH into Google Cloud VM instance](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/domains/ssh-into-vm.png)

2. Install Certbot:
    ```bash
    sudo apt install certbot python3-certbot-apache -y
    ```

3. Run Certbot to obtain and install the certificate:
    ```bash
    sudo certbot --apache --agree-tos --register-unsafely-without-email
    ```
   - `--apache` configures Apache to use the certificate
   - `--agree-tos` automatically accepts the Let's Encrypt terms of service
   - `--register-unsafely-without-email` skips email registration

4. When prompted for domain names, enter them separated by commas:
   - For root + www: `example.com,www.example.com`
   - For subdomain only: `subdomain.example.com`

   ![Certbot domain names prompt](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/domains/certbot-domain-names.png)

After successful installation, you'll see a confirmation message:
![Example of Certbot success message](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/domains/certbot-success-message.png)

That's it! You can now access your API securely over HTTPS.
![Example of accessing app over HTTPS](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/domains/accessing-app-using-domain-name-https.png)


:::info[Automatic Renewal]
Certbot automatically renews your SSL certificate 30 days before expiration. No manual renewal is required.
:::

### I am facing "Some challenges have failed." error while running certbot command. How do I fix it?

If you encounter the "Some challenges have failed" error:

![Example of Certbot error message](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/domains/certbot-error-message.png)

This error is almost always caused by one of two issues:
1. The DNS **A record** doesn't point to the correct VM IP address (common with ephemeral IP addresses)
2. DNS changes haven't propagated across the internet yet

To resolve this error:

1. Find your VM's IP address by running:
   ```bash
   curl icanhazip.com
   ```
2. Log in to your domain registrar and update the DNS A record to point to this IP address

3. Wait 5 minutes for DNS propagation

4. Retry the Certbot command:
    ```bash
    sudo certbot --apache --agree-tos --register-unsafely-without-email
    ```

This should resolve the error and successfully install your SSL certificate.

![Example of Certbot success message](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/domains/certbot-success-message.png)