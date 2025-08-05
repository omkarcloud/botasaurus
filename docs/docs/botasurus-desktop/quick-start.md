---
sidebar_position: 2
---
import LinuxOnly from '@site/src/components/LinuxOnly';

# Quick Start

In the next 10 minutes you'll have two fully-working desktop tools:

**1. Stock-Price Scraper** – Enter a ticker (e.g. AAPL) and get the live price from Yahoo Finance.  
![Stock Scraper Demo](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/stock-scraper-preview.gif)

**2. Amazon PDF-Invoice Extractor** – Drag-and-drop an invoice PDF and extract GST No, Document No, Date and Place of Supply, etc.  
![PDF Extraction Demo](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/pdf-extract-preview.gif)

Both extractors share the same desktop shell, so once you build one, you already know how to build the other—and the next one you have in mind.

## 👨‍💻 Project Setup — Clone, Install, Run

**1️⃣ Clone the Magic 🧙‍♀️:**
```bash
git clone https://github.com/omkarcloud/botasaurus-desktop-starter my-botasaurus-app
cd my-botasaurus-app
```

**2️⃣ Install Packages 📦:**
```bash
npm install
```

**3️⃣ Launch the Desktop App 🚀:**
```bash
npm run dev
```

A window opens with a heading scraper ready to test. Let's explore what you just launched.
<LinuxOnly>
--- 
**Note:** On **Ubuntu 24.04** and later, you will face the following error:

![Sandbox Error](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/quick-start/sandbox-error.png)

To resolve it, run:

```bash
sudo chown root:root ./node_modules/electron/dist/chrome-sandbox
sudo chmod 4755 ./node_modules/electron/dist/chrome-sandbox
```

Then, relaunch the app using:

```bash
npm run dev
```
</LinuxOnly>

## 👀 Touring the Starter App

The starter app demonstrates all the core features through a simple heading scraper:


**1. Home (Input)**  
   - Enter any URL and click Run – the demo scraper grabs the page’s first `<h1>`.  
   ![Input Form](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-desktop-preview.gif)

**2. Results**  
   - See the data returned by the task.
   - Export to CSV / XLSX / JSON.  
   ![Results Table](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-desktop-demo-result.png)

**3. Tasks**  
   - This Page shows all tasks you've started.
   - Abort or delete any task.  
   ![Output Page](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-desktop-demo-tasks.png)

**4. About**  
   - Renders your project’s README.md, servers as app docs.  
   ![About Page](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-desktop-demo-readme.png)


## 📂 Project Structure at a Glance

Before we build our extractors, here's a simplified view of the key files you'll work with:

```
my-botasaurus-app/
├─ assets/                        ← Icons for the installers
├─ inputs/                        
│   └─ scrapeHeadingTask.js       ← Renders UI controls (one file per extractor)
├─ src/
│  └─ scraper/
│      ├─ backend/
│      │   └─ server.ts           ← Central registry – add your scrapers here
│      └─ src/
│          └─ scraper.ts          ← Extraction logic (e.g., grab <h1> with Playwright)
├─ release/                       ← Installers (.exe, .dmg, .deb) after "npm run package"
└─ package.json                   ← Scripts + build settings
```

**Mental model:**  
- `inputs/` = UI controls  
- `src/scraper/src/` = extraction logic  
- `src/scraper/backend/server.ts` = add scraper here

Now that you understand the structure, let's build your first Stock-Price Scraper!