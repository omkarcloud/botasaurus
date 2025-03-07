<a
  target="_blank"
  rel="noopener noreferrer nofollow"
  href="https://camo.githubusercontent.com/4b399104ebd9540801b3284a1a270d2577aa1f0a52331808cd2e450d8ffa6f79/68747470733a2f2f76696577732e77686174696c656172656e65642e746f6461792f76696577732f6769746875622f6f6d6b6172636c6f75642f626f74617361757275732e737667"
  style="opacity: 0; max-height: 0px; display: block"
  ><img src="https://views.whatilearened.today/views/github/omkarcloud/botasaurus-desktop.svg" width="80px" height="28px" alt="View" /></a>

### What is a Desktop Extractor?
A **Desktop Extractor** is a standalone application that runs on your computer and extracts specific data from websites, PDFs, Excel files, and other documents. Unlike web-based tools, desktop extractors run locally, giving **faster performance** and **zero cloud costs**.

![Desktop Extractor showing an application interface with extraction options](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/desktop-app-photo.png)

### What advantages do Desktop Scrapers have over web-based scrapers?
**Desktop Scrapers** offer key advantages over web-based scraper solutions like Outscraper:  

- **Zero Infrastructure Costs**: 
   - Runs on the user's machine, eliminating expensive cloud computing fees.  
   - Lower cloud costs allow you to offer lower pricing, attracting more customers and increasing revenue.

- **Faster Execution**:  
  - Instant execution, no delays for cloud resource allocation.  
  - Uses the user's system, which is much faster than shared cloud servers.  

- **Increased Customer Engagement**:  
  The app sits right on the user's desktop, encouraging frequent use compared to web tools they must actively visit via browser.  

- **Cross-Platform Deployment in 1 Day**:  
  With **Botasaurus**, you can launch a desktop scraper for **Windows, macOS, and Linux** within a day. No need to build a website, manage servers, or handle scaling issues. Bota Desktop includes built-in features such as:
  - Task management
  - Data Table
  - Data export (Excel, CSV, etc.)
  - Sorting & Filtering
  - Caching and many more

With zero usage costs, faster performance, and easier development, Desktop Scrapers outperform web-based alternatives.

### How to Build a Desktop Extractor
Building a Desktop Extractor is easier than you think! All you need is a basic understanding of JavaScript. This guide will walk you through creating two practical extractors:  

- **Yahoo Finance Stock Scraper** – Extracts real-time stock prices from Yahoo Finance.
- **Amazon Invoice PDF Extractor** – Automates the extraction of key invoice data like Document Number, Document Date, and Place of Supply from Amazon PDFs.  

As a web scraper, you might naturally want to focus on web scraping. Still, I want you to create the **Amazon Invoice PDF Extractor** project. Why? Because many developers overlook the immense potential of extracting data from PDFs, Excel files, and other documents.  

**Document Data Extraction is a large untapped market.** For example, even in most developed countries, accountants often spend hundreds of hours manually entering invoice data for tax filings. A desktop extractor can transform this tedious, error-prone process into a task that takes just minutes, delivering 100% accurate results.

Ready to get started? Let’s dive in!

### What Will Be Built, and Why?
We'll create two real-world solutions:

1. **Yahoo Finance Stock Scraper**  
   This tool scrapes **real-time stock prices** from **Yahoo Finance**, demonstrating how to use web scraping tools like Playwright in a desktop app.  

   ![Stock Scraper Demo showing the application extracting stock prices from Yahoo Finance](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/stock-scraper-preview.gif) 

2. **Amazon Invoice PDF Extractor**  
   This tool will **automate the extraction of key invoice data** to save hours of accountants' time:  
   - **Document Number**  
   - **Document Date**  
   - **Place of Supply**  
   - **GST Identification No**  

   ![PDF Extraction Demo showing the application extracting data from Amazon PDF invoices](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/pdf-extract-preview.gif)  

### How to Set Up the Project?
Follow these simple steps to get started:

1️⃣ Clone the Magic 🧙‍♀️:
   ```
   git clone https://github.com/omkarcloud/botasaurus-starter my-botasaurus-desktop-app
   cd my-botasaurus-desktop-app
   ```

2️⃣ Install Packages 📦:
   ```
   npm install
   ```

3️⃣ Launch the App 🚀:
   ```
   npm run dev
   ```

An app will open with a default heading scraper. Enter the link you want to scrape (e.g., `https://example.com/`) and click the **Run** button.

![Starter app interface showing input field and run button](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-desktop-preview.gif)

After a few seconds, the data will be scraped.
![Results screen showing extracted data in a table format](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-desktop-demo-result.png)

Visit the **Output Page** to see the tasks you've started.
![Tasks screen showing history of extraction jobs](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-desktop-demo-tasks.png)

Go to the **About Page** to view the rendered `README.md` file of the project.
![README screen showing documentation in the app](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-desktop-demo-readme.png)

### How Do I Create a Stock Pricer Scraper?
Creating a Stock Pricer Scraper with Botasaurus is a simple 3-step process:

1. **Create your Scraper function** to extract stock prices from Yahoo Finance using Playwright
2. **Add the Scraper to the Server** using 1 line of code
3. **Define the input controls** for the Scraper

Let's dive into the code to understand the process in detail.

#### Step 1: Create the Scraper Function

In `src/scraper/src/scraper.ts`, paste the following code to create `stockPriceScraper` which will:

1. Receive a `data` object and extract the "stock_symbol".
2. Create a link for the Yahoo Finance URL based on the stock symbol.
3. Visit the link using Playwright.
4. Extract the stock price from the page.
![Highlighted Yahoo Finance Element](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/yahoo-finance-element.png)  
5. Return the stock price in a structured format.

Additionally, we name the scraper `stockPriceScraper`, which is required for Botasaurus to find the input controls, which we will create later.

```ts
import { playwright } from 'botasaurus/playwright';

const stockPriceScraper = playwright<any>({
  
  // Run the scraper opening a browser window
  headless: false,
  // Reuse the browser instance for multiple tasks
  reuseDriver: true,
  // Name the scraper for Botasaurus to find inputs
  name: 'stockPriceScraper',
  run: async ({ data, page }) => {
    // Extract the stock symbol from the input data
    const stock_symbol = data['stock_symbol'];
    // stock_symbol the Yahoo Finance URL using the stock symbol
    const link = `https://finance.yahoo.com/quote/${stock_symbol}`;

    // Navigate to the Yahoo Finance page
    await page.goto(link, { waitUntil: 'domcontentloaded' });

    // Extract the stock price using a selector
    const stock_price = parseFloat(
      (await page.textContent('[data-testid="qsp-price"]')) as string,
    );

    // Return the extracted stock price
    return {
      stock_symbol: stock_symbol,
      stock_price: stock_price,
    };
  },
});

export { stockPriceScraper };
```

#### Step 2: Add the Scraper to the Server

In `src/scraper/backend/server.ts`, paste the following code to:
- Import the `stockPriceScraper` function.
- Use `Server.addScraper()` to add the scraper.

```ts
import { Server } from 'botasaurus-server/server'
import { stockPriceScraper } from '../src/scraper'

Server.addScraper(
  stockPriceScraper,
);
```

#### Step 3: Define the Input Controls

Create a new file named `stockPriceScraper.js` in the `inputs` folder and paste the following code. This will:

1. Define a `getInput` function that takes the `controls` parameter.
2. Add a text input control for the stock symbol.
3. Use JSDoc comments to enable IntelliSense Code Completion in VSCode as you won't be able to remember all the controls in botasaurus.

```js
/**
 * @typedef {import('botasaurus-controls').Controls} Controls
 * 
 */

/**
 * @param {Controls} controls
 */
function getInput(controls) {
    controls
        // Render a Text Input
        .text('stock_symbol', { 
            isRequired: true, 
            label: 'Stock Symbol', 
            placeholder: 'Enter a stock symbol (e.g., AAPL)', 
            defaultValue: 'AAPL' 
        });
}
```

![Screenshot of stock symbol input field with AAPL as default](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/stock-input-controls.png)


#### 🎉 You're Done!

You now have a fully functional **Stock Pricer Scraper** that extracts stock prices from Yahoo Finance. 

To test it, simply run `npm run dev` and launch the scraper.

![Stock Scraper Demo showing extraction of AAPL stock price](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/stock-scraper-preview.gif) 

### How Do I Create an Amazon Invoice PDF Extractor?
Let's create an Amazon Invoice PDF Extractor to automatically pull key details like Place of Supply, GSTIN, Document Number, and Document Date from Amazon invoice PDFs. This tool will save a lot of manual effort.

#### Step 1: Install Required Libraries

Install the `electron-pdf-parse` library for PDF parsing, which is a fork of the `pdf-parse` library designed to work seamlessly with Electron.

```bash
npm install electron-pdf-parse
```

#### Step 2: Create the PDF Extractor Function
In `src/scraper/src`, create a file `amazonPdfExtractor.ts` and paste the following code to define the `amazonPdfExtractor` function. This will:
1. Read the PDF file.
2. Extract text from the PDF.
3. Use regex to parse key details like the place of supply, GSTIN, document number, and document date.

```ts
// Import necessary libraries
import fs from "fs"; // For file system operations
import pdf from "electron-pdf-parse"; // For parsing PDF files
import { task } from "botasaurus/task"; // For task management

// Main function to extract data from the PDF text
async function extractFromText(text, pdfPath) {

  // Utility function to format date from 'MM/DD/YYYY' to 'DD-MM-YYYY'
  function formatDate(dateStr) {
    const [month, day, year] = dateStr.split("/");
    return `${day}-${month}-${year}`;
  }

  // Extract place of supply using regex
  const placeOfSupplyMatch = text.match(/Place of supply : ([\w\s]+)\(/);
  // Extract GSTIN using regex (reverse text to find it easily)
  const gstinMatch = text.split("\n").reverse().join("\n").match(
    /GSTIN : (\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d{1}[Z]{1}[A-Z\d]{1})/
  );
  // Extract document number using regex
  const documentNumberMatch = text.match(/Document Number\s*([A-Z0-9]+)/);
  // Extract document date using regex
  const documentDateMatch = text.match(/Document Date\s*(\d{2}\/\d{2}\/\d{4})/);

  // Prepare the results object
  const results = {
    "Place of Supply": placeOfSupplyMatch ? placeOfSupplyMatch[1].trim() : null,
    GSTIN: gstinMatch ? gstinMatch[1] : null,
    "Document Number": documentNumberMatch ? documentNumberMatch[1] : null,
    "Document Date": documentDateMatch
      ? formatDate(documentDateMatch[1])
      : null,
  };

  return results;
}

// Function to read and extract data from a PDF file
async function extractData(pdfPath) {
  const dataBuffer = fs.readFileSync(pdfPath); // Read the PDF file
  const data = await pdf(dataBuffer); // Parse the PDF
  return extractFromText(data.text, pdfPath); // Extract data from the parsed text
}

// Task definition for the Amazon PDF Extractor
export const amazonPdfExtractor = task<any>({
  name: "amazonPdfExtractor", // Name of the task
  run: async function ({ data }) {
    const files = data["files"]; // Get the list of files to process
    const results: any[] = []; // Array to store results

    // Process each file
    for (const file of files) {
      try {
        const result = await extractData(file.path); // Extract data from the PDF
        results.push(result); // Add the result to the array
      } catch (error: any) {
        console.error(error); // Log any errors
        results.push({ failed: file, error: error.toString() }); // Add error details to results
      }
    }
    return results; // Return the results
  },
});
```

#### Step 3: Add the Extractor to the Server

In `src/scraper/backend/server.ts`, add the following code to:
- Import the `amazonPdfExtractor` function.
- Use `Server.addScraper()` to add the scraper.

```ts
import { amazonPdfExtractor } from '../src/amazonPdfExtractor';

Server.addScraper(
  amazonPdfExtractor,
);
```

#### Step 4: Define the Input Controls

Create a new file named `amazonPdfExtractor.js` in the `inputs` folder and paste the following code. This will:

1. Define a `getInput` function that takes the `controls` parameter.
2. Add a file picker for selecting the Amazon invoice PDFs.

```js
/**
 * @typedef {import('botasaurus-controls').Controls} Controls
 * @typedef {import('botasaurus-controls').FileTypes} FileTypes
 * 
 */

const { FileTypes } = require('botasaurus-controls')

/**
 * @param {Controls} controls
 */
function getInput(controls) {
    // Render a File Input for uploading PDFs
    controls.filePicker('files', {
      label: "Files",
      accept: FileTypes.PDF, 
      isRequired: true,
    })
}
```
![File picker interface for PDF selection](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/pdf-file-picker.png)

That's it! You now have a fully functional **Amazon Invoice PDF Extractor** ready to use. 

To test the extractor:
1. Download a sample Amazon invoice PDF from [here](https://raw.githubusercontent.com/omkarcloud/botasaurus-desktop-tutorial/master/test/sample-invoice.pdf).  
2. Click the **Amazon PDF Extractor** button.  
   ![choose-the-amazon-pdf-extractor-button](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/choose-the-amazon-pdf-extractor-button.png)  
3. Upload the PDF and run the extractor to see the extracted data.

![PDF Extraction Demo showing the process of extracting data from an Amazon invoice](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/pdf-extract-preview.gif)  

You can find the complete code for this tutorial, including the **Stock Pricer Scraper** and **Amazon Invoice PDF Extractor**, in the [Botasaurus Desktop Tutorial GitHub Repository](https://github.com/omkarcloud/botasaurus-desktop-tutorial).

### How do I create executable installers for my OS?
To create an installer for your operating system, run the following command:
```bash
npm run package
```

After executing the command, you can find the installer for your OS in the `release/build` folder.

![Screenshot of release/build folder with OS-specific installer](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/installer-build-folder.png)

**Note**  
On Windows, if you face the "resource busy or locked" error:

![Resource Busy](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/resource-busy.png)  

Please follow these steps to resolve the issue:
1. Run the Command Prompt as an Administrator.
2. 'cd' to your project directory.
3. Run the command `npm run package` again to create the installer.

This will resolve the error and allow the installer to be created successfully.

### How do I create installers for multiple platforms?
We need to create 4 installers for your app:
- `.dmg` for macOS
- `.exe` for Windows
- `.deb` for Ubuntu/Debian
- `.rpm` for Fedora/CentOS/Red Hat

To create each installer, we need to run the 'package' script on each OS. You can imagine how inconvenient it would be to get machines with all these operating systems.

So we will automate this using **GitHub Actions**. This workflow will:
- Be triggered every time you push code to GitHub.
- Build the installers for all these platforms automatically.
- Upload them to an **AWS S3 bucket**.

Please follow these steps:

**1. GitHub Repository Setup**
1. Create a new repository on GitHub to host your application.
![new-repo-bota](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/new-repo-bota.png)

**2. Create an S3 Bucket**
1. Open the AWS Console > S3.
![aws-s3](https://raw.githubusercontent.com/omkarcloud/macos-code-signing-example/master/images/aws-s3.png)  
2. Click "Create bucket".
![create-bucket](https://raw.githubusercontent.com/omkarcloud/macos-code-signing-example/master/images/s3-bucket-setup.jpg)  
3. Configure the bucket:
```
Bucket name: Enter a unique bucket name. Conventionally, this name matches your product's name in kebab case. For example, if your product's name is "Yahoo Finance Extractor," your bucket name will be `yahoo-finance-extractor`.
Object Ownership: Select ACLs enabled
Block Public Access settings for this bucket: Uncheck "Block all public access"
```
*Important Note:*
Ensure that **Object Ownership** is set to **"ACLs enabled"** because Electron Builder requires this setting to successfully upload files. Without it, you will encounter the following error:

**"The Bucket does not allow ACLs."**  

![ACL Error](https://raw.githubusercontent.com/omkarcloud/macos-code-signing-example/master/images/acl-error.png)

4. Click on "Create bucket".
![S3 Bucket Creation](https://raw.githubusercontent.com/omkarcloud/macos-code-signing-example/master/images/s3-bucket-setup.jpg)

5. If you don't have an AWS access key and secret key, create them through the IAM service as described in [AWS documentation here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user_manage_add-key.html).

**3. Configure GitHub Secrets**
In your GitHub Repository, navigate to Settings > Secrets and variables > Actions > Repository secrets and add the following secrets:
```
AWS_ACCESS_KEY_ID            # AWS access key
AWS_SECRET_ACCESS_KEY        # AWS secret key
```

![GitHub Secrets](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/github-secrets.png)


**4. Configure Electron Builder**
1. In your project's "package.json" file, add the following to the Electron "build" configuration:
```json
"build": {
  "publish": {
    "provider": "s3",
    "bucket": "todo-my-bucket-name"
  }
}
```
Replace `todo-my-bucket-name` with the name of your S3 bucket. 

**5. Deploy**
1. Push the code to your GitHub repository.
2. Go to the repository's "Actions" tab to see the build process in action.
![GitHub Actions Workflow](https://raw.githubusercontent.com/omkarcloud/macos-code-signing-example/master/images/github-actions.jpg)
3. After a successful build, the installer files will be found in your S3 bucket. These files will be publicly accessible in the following format:
```
https://<your-bucket-name>.s3.amazonaws.com/<your-product-name>.dmg
```

Examples:
- https://yahoo-finance-extractor.s3.amazonaws.com/Yahoo+Finance+Extractor.dmg
- https://yahoo-finance-extractor.s3.amazonaws.com/Yahoo+Finance+Extractor.exe
- https://yahoo-finance-extractor.s3.amazonaws.com/Yahoo+Finance+Extractor.deb
- https://yahoo-finance-extractor.s3.amazonaws.com/Yahoo+Finance+Extractor.rpm

### What is code signing?
Apple and Microsoft both want to ensure that the apps running on their OS are safe and don't contain any viruses. So they have a process called code signing, in which they will:
- Verify your identity
- Scan your code for any viruses
- Once they are sure that your code is safe, they will sign it with a certificate, which tells the OS that this app is safe to run.

### What if I don't sign my app?

- **macOS:** Users **will not** be able to install your app.

![macOS warning dialog showing "App cannot be opened because the developer cannot be verified"](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/macos-security-warning.webp)

- **Windows:** Users can install your app, but will see a warning popup saying Windows Defender blocked an unknown publisher. To proceed, they must click **"More Info"** and then select **"Run Anyway"**.

![Windows SmartScreen warning showing "Windows protected your PC" message for unsigned application](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/windows-smartscreen-warning.png)

- **Linux:** There will be no warnings, so users can install and run your app without any issues.

**Note:** On Mac and Windows, if you build the installer using `'npm run package'` and install it on the same machine, you won't see any security popups. However, if you run the unsigned installer on a different PC where it wasn't built (e.g., a friend's PC), security warning popups will appear.

### How to do Code Signing for Mac?
To Code Sign for Mac, you need:
- A system running macOS
- A subscription to the [Developer Program by Apple](https://developer.apple.com/support/compare-memberships/), which costs $99 per year

Once you have those, please watch this YouTube video to learn how to do code signing for Mac:

[![Macos Code Signing Example Video](https://raw.githubusercontent.com/omkarcloud/macos-code-signing-example/master/images/macos-code-signing-example-video.png)](https://www.youtube.com/watch?v=hYBLfjT57hU)

### How to Do Code Signing for Windows?
Coming in **2-3 months**.

### Can I use the same code signing certificate for multiple apps?  
Yes, you can use the same code signing certificate to sign unlimited apps. For example, you can use it to sign multiple scraping tools.

### Code signing is quite expensive. Is there a cost-effective alternative for an early-stage developer?  
Yes, it is expensive, and for early-stage developers, it would be financially unwise to invest in a certificate when your app has no users yet. 

If you're just starting out, here's a way to launch with minimal upfront costs:

1. **Temporarily Adjust Your App Download Page as follows:**  
   - **For macOS:** Do not provide a download link.  
   - **For Windows:** Provide the download link, but include a message like this:  
     *"Temporarily, you will see a blue popup from Windows Defender stating that the app is from an **unknown publisher**. This is because we are not yet a verified publisher. Rest assured, the app is 100% safe. To proceed, click 'More Info' and then 'Run Anyway.' We aim to become a verified publisher soon to resolve this."*  
2. Dedicate your efforts to promoting your app and building a user base.  
3. Once you have enough users, monetize it.  
4. After a few months, when your app is generating revenue, you can invest in a code signing certificate and sign your app.  
   
**Why this is financially wise?**  
This strategy allows you to start with minimal upfront costs and only invest in code signing once your app is generating revenue.

### Is there anything else I need to do before launching my app to the public?  
Before making your app public, follow these steps to ensure a perfect launch:  

#### 1. Replace Placeholder Text  
Search your project for the following placeholders and update them with your actual values:  

| Placeholder | Example Replacement |
|-------------|--------------------|
| `todo-my-app-name` | `amazon-invoice-pdf-extractor` |
| `Todo My App Name` | `Amazon Invoice PDF Extractor` |
| `Todo my app description` | `Extract data from Amazon PDFs quickly and accurately.` |
| `todo-my-organization-name` | `head-first` |  
| `Todo My Organization Name` | `Head First` |  
| `todo-my-email@gmail.com` | `head-first-python@gmail.com` |

#### 2. Replace Icon Assets
Replace the placeholder icons with your brand assets. These icons are used when creating installers for your app:

1. `assets/icons/16x16.png`
2. `assets/icons/24x24.png`
3. `assets/icons/32x32.png`
4. `assets/icons/48x48.png`
5. `assets/icons/64x64.png`
6. `assets/icons/96x96.png`
7. `assets/icons/128x128.png`
8. `assets/icons/256x256.png`
9. `assets/icons/512x512.png`
10. `assets/icons/1024x1024.png`
11. `assets/icon.icns`
12. `assets/icon.ico`
13. `assets/icon.png`
14. `public/icon-256x256.png`

**Recommended Workflow to Create Them:**
1. Use [Figma](https://www.figma.com/) to design your app icon.
2. Export your icon from Figma in all the required PNG sizes.
3. Generate platform-specific icon formats:
   - For macOS, use [CloudConvert PNG to ICNS](https://cloudconvert.com/png-to-icns) to generate `assets/icon.icns`. Upload the `assets/icons/1024x1024.png` file, which is the [recommended size for macOS app icons](https://www.electronforge.io/guides/create-and-add-icons).
   - For Windows, use [FreeConvert PNG to ICO](https://www.freeconvert.com/png-to-ico) to create `assets/icon.ico`. Upload the `assets/icons/256x256.png` file, which is the [recommended size for Windows app icons](https://www.electronforge.io/guides/create-and-add-icons).
4. Replace all the listed files with your new brand assets.
5. Save the following icons in a secure location, as you will need them in the future for your organization's LinkedIn, Twitter, or other social media profiles:
   - `assets/icons/256x256.png`
   - `assets/icons/512x512.png`
   - `assets/icons/1024x1024.png`

**Alternative Approach:**
If you don't have a brand icon yet and don't want to invest time in creating one, you can continue using the existing icons (they are professional). This allows you to launch faster with a polished appearance. Once you have users, you can invest time in creating a custom icon.

#### 3. Increment Your App Version  
Run the following command to update the app version:  
```sh
node increment-version.js
```

#### 4. Add Customer Support Options  
Providing customer support will greatly enhance user experience. We recommend adding both **WhatsApp** and **Email** support. Based on our experience, customers often prefer WhatsApp over email.  

Your support options will appear in the **top menu bar** of your app:  

![Support Menu Example showing WhatsApp and Email options](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/support-menu-example.png)  

**Adding WhatsApp Support**  
To enable WhatsApp support, update `src/scraper/backend/server.ts` with the following code:  
```ts
import { Server } from 'botasaurus-server/server';
import { config } from '../../main/config';

// Add WhatsApp support details
Server.addWhatsAppSupport({
  number: '1234567890', // Your 10-digit phone number (without the country code)
  countryCallingCode: '81', // Your country calling code (e.g., 81 for Japan, 1 for the US)
  message: `Hi, I need help with using the ${config.productName} Tool`, // Default message for WhatsApp
});
```

**Adding Email Support**  
Similarly, to enable email support, add the following code to `src/scraper/backend/server.ts`:  
```ts
import { Server } from 'botasaurus-server/server';
import { config } from '../../main/config';

// Add Email support details
Server.addEmailSupport({
  email: 'happy.to.help@my-app.com', // Replace with your support email
  subject: `Help with ${config.productName} Tool`, // Default email subject
  body: `Hi, I need help with using the ${config.productName} Tool`, // Default email body
});
```

**🎉 That's it! You're all set! Now go!** 🚀  
- Create something amazing that helps people.  
- Market it well, so it reaches people.  
- Achieve financial freedom and live life on your terms!  

Wishing you all the success in life!