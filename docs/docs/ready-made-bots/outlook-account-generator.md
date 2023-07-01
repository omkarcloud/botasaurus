---
sidebar_position: 20
label: Outlook Account Generator

---
# Outlook Account Generator

<p align="center">
  <img src="https://raw.githubusercontent.com/omkarcloud/outlook-account-generator/master/images/outlook.png" alt="outlook" />
</p>
  <div align="center" style={{ marginTop: 0 }}>
  <p>💦 Enjoy the Rain of Outlook Accounts 💦</p>
</div>
<em>
  <h5 align="center">(Programming Language - Python 3)</h5>
</em>
<p align="center">
  <a href="#">
    <img alt="outlook-account-generator forks" src="https://img.shields.io/github/forks/omkarcloud/outlook-account-generator?style=for-the-badge" />
  </a>
  <a href="#">
    <img alt="Repo stars" src="https://img.shields.io/github/stars/omkarcloud/outlook-account-generator?style=for-the-badge&color=yellow" />
  </a>
  <a href="#">
    <img alt="outlook-account-generator License" src="https://img.shields.io/github/license/omkarcloud/outlook-account-generator?color=orange&style=for-the-badge" />
  </a>
  <a href="https://github.com/omkarcloud/outlook-account-generator/issues">
    <img alt="issues" src="https://img.shields.io/github/issues/omkarcloud/outlook-account-generator?color=purple&style=for-the-badge" />
  </a>
</p>
<p align="center">
  <img src="https://views.whatilearened.today/views/github/omkarcloud/outlook-account-generator.svg" width="80px" height="28px" alt="View" />
</p>

---

🌟 Create Multiple Outlook Accounts with Ease! 🤖

## ✨ Why Choose This Bot?

🌍 Generate Realistic Account Details: Obtain authentic names, usernames, and passwords based on your country of residence.

💾 Save Account Details as JSON: Every created account is conveniently saved in JSON format, making it easy to access and manage the account information.

⚡ Lightning Fast: This bot is designed for speed, allowing you to generate multiple Outlook accounts quickly and efficiently.

🔒 Anti Bot Detection: The bot incorporates measures to bypass detection, ensuring a smooth account creation process.

🖥️ Chrome Profile Storage: Each created account is saved as a profile, enabling you to access your Outlook users anytime without the need for login credentials.

![Profiles](https://raw.githubusercontent.com/omkarcloud/outlook-account-generator/master/images/profiles.png)

## 🚀 Getting Started

1️⃣ Clone the Magic 🧙‍♀️:

```shell
git clone https://github.com/omkarcloud/outlook-account-generator
cd outlook-account-generator
```

2️⃣ Install Dependencies 📦:

```shell
python -m pip install -r requirements.txt
```

3️⃣ Let the Rain of Outlook Accounts Begin 😎:

```shell
python main.py
```

The bot will take care of filling in the required details automatically. You will only be prompted to solve the captcha manually.

By manually solving the captcha, there's no need to purchase additional captcha-solving services or proxies to run the bot.

![Profiles](https://raw.githubusercontent.com/omkarcloud/outlook-account-generator/master/images/solve-captcha.png)

_Once Bot is Completed Running. The Accounts will be saved in `profiles.json`_

## 🎥 Video Demo

Watch this video to see the bot in action!

<!-- TODO:

[![Outlook Account Generator](./screenshots/outlook-account-generator.png)](https://www.youtube.com/watch?v=zOlvYakogSU) -->

## 🤔 FAQs

❓ **It is generating only 3

 accounts. How can I generate more than 3 accounts?**

Open `src/config.py` and specify the number of accounts you want to generate. For example, to generate 100 accounts, use the following code:

```python
config = {
    "number_of_accounts_to_generate": 100
}
```

❓ **Why are you not using proxies and captcha-solving services to solve captchas?**

I attempted to solve the captcha using 2captcha, but unfortunately, it proved to be unsolvable. This issue arises because the location where the account is being created differs from the location where the captcha is being solved. The captcha system detects this mismatch, causing the captcha prompt to appear repeatedly in a loop.

The bot will automatically prompt you when a captcha needs to be solved.

❓ **Why am I prompted to change my IP address?**

After using the bot to create a few accounts and becoming familiar with how it works, the bot will prompt you to change the IP address after each account creation.

![Change Ip](https://raw.githubusercontent.com/omkarcloud/outlook-account-generator/master/images/change-ip.png)

The reason we want you to change your IP is that if you create multiple accounts with a single IP, Microsoft will notice that multiple accounts were created from the same IP address. As a result, Microsoft may suspend these accounts after a few days.

To protect your account from being suspended, we prompt you to change the IP address, ensuring that a single account is created from a single IP.

Changing your IP is an easy process. To learn about multiple methods to change your IP address, visit this [link](https://www.omkar.cloud/bose/docs/guides/change-ip/)

Furthermore, one of the most effective methods for changing the IP is the **Enable and Disable Airplane Mode** technique outlined below:

1. Connect your PC to a mobile hotspot.
2. On your mobile device, turn airplane mode on and off.
3. Now, turn the hotspot on again.
4. You will get a new IP assigned.

❓ **The code is well-structured and organized. Most Selenium codebases are messy. How did you do it?**

I use the Bose Framework, a Bot Development Framework that greatly simplifies the process of creating bots.

The Outlook Account Generator uses Bose to:

1. Generate account details
2. Maintain code structure
3. Enable running the bot multiple times
4. Prompt to change IP
5. Save account details in profiles
6. Incorporate anti-bot detection features
7. Utilize the enhanced Selenium Driver to reduce code.

Without Bose Framework, it would be 2x more harder to make this Outlook Account Generator.

You can see `outlook_sign_up_task.py` to understand the simplicity Bose Brings.

Explore the Bose Framework [here](https://www.omkar.cloud/bose/).

❓ **What is the purpose of the "visit_outlook_accounts_task"?**

After creating each account, it is saved as a profile.

We use the `visit_outlook_accounts_task` to open each Outlook account in the browser. To use the `visit_outlook_accounts_task`, please open the `__init__.py` file and paste the following code:

```python
from .visit_outlook_accounts_task import VisitOutlookAccountsTask
from .outlook_sign_up_task import OutlookSignUpTask

tasks_to_be_run = [
        VisitOutlookAccountsTask,
        # OutlookSignUpTask,
]
```

❓ **How can I thank you?**

Star ⭐ the repository.

Your star will send me a Telegram Notification, and it will bring a smile to my face :)

❓ **I'm interested in creating more bots. Can you assist me?**

Certainly! As a professional scraper, I'd

 be delighted to discuss your requirements further. Feel free to reach out to me at chetan@omkar.cloud.

## _PS: I have a great suggestion for you. You probably use Outlook accounts to log into some website and automate actions, Isn't it? I recommend using the Bose Framework for writing your automation code directly in this repository. This will really save you a large chunk of development time._

---

## Love It? Star It! ⭐
