---
sidebar_position: 26
---

# Understanding App Features
This guide explains the Support Menu and the Auto Update system.

## Support Menu

The Support Menu, located in the top-right corner of the app, provides options for debugging, resetting the app, and getting support.

It contains the following options:
![Support Menu](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/understanding-app-features/support-menu.png)

Here’s a breakdown of each option:

### Show User Data

Opens the folder containing all application data, which is useful for debugging any issues your users encounter in production.

It includes:

-   **`task_results/`**: Stores cached data and scraped results.
-   **`botasaurus_storage.json`**: Persistent JSON storage for user settings. You can also use this storage in your code as follows:
    ```javascript
    import { getBotasaurusStorage } from 'botasaurus/botasaurus-storage';

    const storage = getBotasaurusStorage();
    
    storage.setItem('userId', 10);
    const userId = storage.getItem('userId');
    ```
-   **`db.nedb`**: The application's database.

> **Note:** These files appear in your root folder when running the app in development (`npm run dev`).

### Factory Reset App and Clear All Data

Resets the app to its original state by deleting:  
- `task_results/`  
- `botasaurus_storage.json`  
- `db.nedb`

**When to use:**
- To free up storage space
- To start with a clean installation

When clicked, the app will request confirmation before deleting any data.
![Factory Reset Confirmation](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/understanding-app-features/factory-reset-confirmation.png)

### Update to Latest Version

Manually checks for updates and installs the latest version if the app is not already up-to-date.

### Contact Support via WhatsApp & Contact Support via Email

These options provide your users with direct ways to contact you for help.

-   **Contact Support via WhatsApp**: Opens WhatsApp Web in the user's browser with a pre-filled message.
-   **Contact Support via Email**: Launches the user's default email app with a pre-filled message.

![Contact Support](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/understanding-app-features/contact-support.png)

You can learn how to configure these with your contact details in the [Pre-Launch Checklist](./pre-launch-checklist.md) section.

## Auto Updates

Botasaurus Desktop automatically updates itself when new versions are released. This ensures your users always have the latest features and bug fixes without manual installation.

To enable this feature, you need to host your application installers on an **AWS S3 bucket**, as detailed in the [Packaging & Publishing guide](./packaging-publishing.md).

Once configured, pushing new code to your GitHub repository will trigger a new build. The application will then automatically update itself, on next app launch.

Auto updates are supported on the following platforms:
-   **macOS**
-   **Windows**: Only supported when the app is signed with a code signing certificate.
-   **Linux**