---
sidebar_position: 3
---

# Windows Code Signing Guide

This guide explains the two main options for obtaining a Windows code signing certificate.

## ✅ If You're Based in the US or Canada

**If your business is in the US or Canada and has 3+ years of tax history**, the best option is **Azure Trusted Signing** — it's the cheapest at just **\$10/month**.

For a detailed walkthrough, follow this excellent guide: **[Code Signing on Windows with Azure Trusted Signing by melatonin.dev](https://melatonin.dev/blog/code-signing-on-windows-with-azure-trusted-signing/)**

## 🌍 For Everyone Else
You will need an **Extended Validation (EV) Code Signing Certificate** (not an Organization Validation (OV)) from a Certification Authority (CA) like DigiCert or Sectigo.

### Important Requirements

Code signing requirements are stringent and designed for companies — **not solo developers**. While requirements vary by country, here are the standard ones:

- **Registered Business:** You must be a legally registered company. (Sole proprietorships usually don't qualify, but check with your chosen CA to confirm.)
- **Physical Address:** A physical business address (not a P.O. box or virtual office). This address should be listed in public records like Google Maps or DUNS.
- **Professional Web Presence:** A business website and a company email address (e.g., `your.name@yourcompany.com`) are required. Personal email addresses (such as Gmail or Outlook) will not be accepted for registration.

:::warning[Contact Sales Before You Purchase]
Contact the CA's validation or sales team to ask exactly which documents are required for your country and entity type. 

Don't purchase first and then ask about the requirements, as I did. In my case, it led to a failed validation — a waste of time I hope you can avoid.
:::

### Use Cloud Signing

When purchasing your certificate, select the "Cloud Signing" or "Cloud HSM" option. While more expensive than hardware tokens, it enables automated signing in GitHub Actions and avoids hardware token hassles. For example, DigiCert's cloud-based EV certificate costs $1,068 per year.

### Recommended Certification Provider

If you're wondering which CA to choose, we recommend DigiCert despite their higher cost ($1,068 for EV Cloud Signing) for these reasons:

- DigiCert is the most popular CA. Following the wisdom of the crowd makes it a safe choice.
    - Electron uses DigiCert [to sign their applications](https://www.electronjs.org/docs/latest/tutorial/code-signing#signing-windows-builds).
    ![Electron build signed with a DigiCert certificate](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/code-signing/electron-sign.png)
    - The popular npm package **[@electron/windows-sign](https://github.com/electron/windows-sign)**, used for signing Windows executables, features DigiCert extensively in its documentation.
    ![Documentation for @electron/windows-sign showing DigiCert examples](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/code-signing/windows-sign.png)

- They offer a 30-day refund policy, which is a key benefit if you're unsure whether you'll pass the validation process. I attempted to obtain an EV Certificate through DigiCert but failed validation because I wasn't registered as a company, which is required for Indian businesses. They refunded my payment within a few days.

:::info[Note for Solo Developers] 
We recommend DigiCert because it's the wisdom-of-the-crowd option. We were not paid by DigiCert. 

CA Code Signing is definitely too expensive, and I wouldn't recommend the CA Code Signing process if you're just starting out. 
:::

## ✅ Final Recommendation

- If you're an American or Canadian business with **3+ years of tax history** (or have a family member or friend with such a business), choose **Azure Trusted Signing** (\$120/year).

- Otherwise, if you qualify and can afford it, go with **DigiCert EV Cloud Code Signing** ($1,068/year). To proceed:

    1. First, contact DigiCert's Validation Team to confirm the specific requirements for your country and entity type [here](https://www.digicert.com/support). 

    ![digicert validation](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/code-signing/digicert-validation.png)
    
    Send them this message via chat, replacing YOUR_COUNTRY and YOUR_ENTITY_TYPE with your details:
    ```
    Kindly share the documents required specifically for YOUR_COUNTRY, registered as YOUR_ENTITY_TYPE, for obtaining an EV Code Signing Certificate. 
    ```
    
    2. Once you've confirmed you can meet the requirements, purchase the certificate from this link, which has the Cloud Signing EV option pre-selected:
    
    https://www.digicert.com/signing/code-signing-certificates#code_signing_ev_key_locker