---
sidebar_position: 31
---
import ShortCut from '@site/src/components/ShortCut';

# Pre-Launch Checklist

Before making your app public, follow these steps to ensure a perfect launch:  

### 1. Replace Placeholder Text

Search your codebase for the following placeholders and replace them with your app's actual details:

| Placeholder                 | Example Replacement                                                       |
| --------------------------- | ------------------------------------------------------------------------- |
| `todo-my-app-name`          | `yahoo-finance-extractor`                                                 |
| `Todo My App Name`          | `Yahoo Finance Extractor`                                                 |
| `Todo my app description`   | `Extract real-time stock prices from Yahoo Finance quickly and accurately.` |
| `todo-my-organization-name` | `head-first`                                                              |
| `Todo My Organization Name` | `Head First`                                                              |
| `todo-my-email@gmail.com`   | `head-first-python@gmail.com`                                             |

:::tip[Use Find & Replace All]
Use your IDE's global search feature (<ShortCut/>+Shift+F) to replace all placeholder text across your codebase.

![Find and Replace Example](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/pre-launch-checklist/find-replace-example.png)
:::

### 2. Upload to S3

If you haven't already, [upload installers to S3](./packaging-publishing.md)

### 3. Replace Icon Assets

Replace default icons with your own brand icons. 

You will need to create the following icons:

**Standard PNG Icons:**
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

**Platform-Specific Icons:**
1. `assets/icon.icns` (macOS)
2. `assets/icon.ico` (Windows)
3. `assets/icon.png` (Linux)

**Web Assets:**
1. `public/icon-256x256.png`



#### How to Create Icons

**Step 1: Design Your Icon**
1. Use [Figma](https://www.figma.com/) or another design tool to create your app icon

**Step 2: Export PNG Icons**

Export your icon into the following PNG sizes and place them in the appropriate folders:

  In `assets/icons/`:
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

  In `public/`
    1. `public/icon-256x256.png`

**Step 3: Generate Platform-Specific Icons**

**For macOS (.icns):**
- Go to [CloudConvert PNG to ICNS](https://cloudconvert.com/png-to-icns)
- Upload `assets/icons/1024x1024.png` file ([recommended size for macOS](https://www.electronforge.io/guides/create-and-add-icons#supported-formats))
- Save as `assets/icon.icns`

**For Windows (.ico):**
- Go to [FreeConvert PNG to ICO](https://www.freeconvert.com/png-to-ico)
- Upload `assets/icons/256x256.png` file ([recommended size for Windows](https://www.electronforge.io/guides/create-and-add-icons#supported-formats))
- Save as `assets/icon.ico`

**For Linux:**
- Copy `assets/icons/256x256.png` to `assets/icon.png`.

**Step 4: Backup Icons**

Save the following icons in a secure location.

- `assets/icons/256x256.png` 
- `assets/icons/512x512.png`
- `assets/icons/1024x1024.png`

You will need them for your organization's LinkedIn, Twitter, your website, and other marketing materials.


:::info[Quick Launch Alternative]
If you don't have a brand icon yet and don't want to invest time in creating one, you can use the existing default icons, they're professional-looking. This allows you to launch faster with a polished appearance. 

Once you have users, you can invest time in creating a custom icon.
:::

### 4. Add Customer Support

Giving great customer support is your duty. Give it your best shot.

I recommend offering not only email but also WhatsApp, as most users prefer WhatsApp over email.

We provide WhatsApp support for our apps, and users appreciate it.


Your support options will appear in your app's **Support** menu:

![Support menu showing WhatsApp and Email options](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/support-menu-example.png)


#### Adding WhatsApp Support

To add WhatsApp support, update `src/scraper/backend/server.ts` with the following code:

```ts title="src/scraper/backend/server.ts"
import { Server } from 'botasaurus-server/server';
import { config } from '../../main/config';

// highlight-start
// Add WhatsApp support details
Server.addWhatsAppSupport({
  number: '1234567890', // Your 10-digit phone number (without the country code)
  countryCallingCode: '81', // Your country calling code (e.g., 81 for Japan, 1 for US)
  message: `Hi, I need help with using the ${config.productName} Tool`, // Default message for WhatsApp
});
// highlight-end
```

#### Adding Email Support

Similarly to add email support, update `src/scraper/backend/server.ts` with the following code:  

```ts title="src/scraper/backend/server.ts"
import { Server } from 'botasaurus-server/server';
import { config } from '../../main/config';

// highlight-start
// Add Email support details
Server.addEmailSupport({
  email: 'happy.to.help@my-app.com', // Replace with your support email
  subject: `Help with ${config.productName} Tool`, // Default email subject
  body: `Hi, I need help with using the ${config.productName} Tool`, // Default email body
});
// highlight-end
```

#### Add Support Section to Product Page

It's a best practice to add a dedicated support section to your product page. You can adapt the following template, which has proven effective for us.

To customize the template:
- Replace `811234567890` with your full WhatsApp number (country code + phone number).
- Replace `happy.to.help@my-app.com` with your support email.
- Replace `Yahoo%20Finance%20Extractor` with your product name, with spaces replaced by `%20`.


```markdown
### ❓ Need More Help or Have Additional Questions?

For further help, feel free to contact us via:

- **WhatsApp:** If you prefer WhatsApp, simply message us [here](https://api.whatsapp.com/send?phone=811234567890&text=I%20need%20help%20with%20using%20the%20Yahoo%20Finance%20Extractor%20Tool.). Please include as much detail as possible so we can help you effectively.

  [![Contact Us on WhatsApp about Google Maps Scraper](https://raw.githubusercontent.com/omkarcloud/assets/master/images/whatsapp-us.png)](https://api.whatsapp.com/send?phone=811234567890&text=I%20need%20help%20with%20using%20the%20Yahoo%20Finance%20Extractor%20Tool.)

- **Email:** Prefer email? Send your questions to [happy.to.help@my-app.com](mailto:happy.to.help@my-app.com?subject=Help%20with%20Yahoo%20Finance%20Extractor%20Tool&body=I%20need%20help%20with%20using%20the%20Yahoo%20Finance%20Extractor%20Tool.). Also, please include as much detail as possible so we can help you effectively.

  [![Contact Us on Email about Google Maps Scraper](https://raw.githubusercontent.com/omkarcloud/assets/master/images/ask-on-email.png)](mailto:happy.to.help@my-app.com?subject=Help%20with%20Yahoo%20Finance%20Extractor%20Tool&body=I%20need%20help%20with%20using%20the%20Yahoo%20Finance%20Extractor%20Tool.)

We look forward to helping you and will reply within 1 working day.
```

**Preview:**

![Support Section Example](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/pre-launch-checklist/support-section-example.png)


> 💡 Once you start getting lots of support queries, consider hiring a support agent and writing an SOP (Standard Operating Procedure) to help them respond effectively.

**🎉 That's it! You're all set! Now go!** 🚀  
- Create something amazing that helps people.  
- Market it well, so it reaches people.  
- Achieve financial freedom and live life on your own terms!  

Wishing you all the success in life!