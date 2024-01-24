---
sidebar_position: 1.1
title: Sign Up Features
---

# Sign Up Features

## How to Generate Human-Like User Data?

To create human-like user data, use the `generate_user` function:

```python
user = bt.generate_user(country=bt.Country.IN)
```

This will generate user profiles similar to the one shown below:

![Account](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/generated-account.png)

The data generated is very realistic, reducing the likelihood of being flagged as a bot.

## The Target Website Has Sent a Verification Email: How to Get the Link and Verify It?

To get the verification link from an email and then delete the mailbox, use `bt.TempMail.get_email_link_and_delete_mailbox` as shown below:

```python
user = bt.generate_user(country=bt.Country.IN)
email = user["email"]  # Example: madhumitachavare@1974.icznn.com

link = bt.TempMail.get_email_link_and_delete_mailbox(email)  # Retrieves the Verification Link and Deletes the Mailbox

driver.get(link)
```

## I have automated the Creation of User Account's. Now I want to store the User Account Credentials like Email and Password. How to store it?

To store user-related data, such as account credentials, use the `ProfileManager` module:

```python
bt.Profile.set_profile(user)
```

In cases where you want to store metadata related to a user, such as API keys:

```python
bt.Profile.set_item("api_key", "BDEC26...")
```

To retrieve a list of all users, use `bt.Profile.get_all_profiles()`:

```python
profiles = bt.Profile.get_all_profiles()
```

## The Chrome Profiles of User's are getting very large like 100MBs, is there a way to Compress them? 

You can use tiny_profile feautre of Botasaurus which are a replacement for Chrome Profiles.

Each Tiny Profile only stores cookies from visited websites, making them extremely lightweight—around 1KB. Here's how to use them:

```python
@browser(
    tiny_profile=True, 
    profile='my-profile',
)
def sign_up_task(driver: AntiDetectDriver, data):
    # Your sign-up code here
```

## How to Dynamically Specify the Profile Based on a Data Item?

You can dynamically select a profile by passing a function to the `profile` option, which will receive the data item:

```python

def get_profile(data):
    return data["username"]

@browser(
    data=[{"username": "mahendra-singh-dhoni", ...}, {"username": "virender-sehwag", ...}],
    profile=get_profile,
)
def sign_up_task(driver: AntiDetectDriver, data):
    # Your sign-up code here
```

user_agent, proxy, and other options can also be passed as functions.

## Is there a Tutorial that integrates tiny_profile, temp mail, user generator, profile to sign up on a Website and Perform Actions on Website. So I can get a Complete Picture?

For a comprehensive guide on using Botasaurus features such as `tiny_profile`, `temp_mail`, `user_generator`, and `profile` to sign up on a website and perform actions, read the Sign-Up Tutorial [Here](https://www.omkar.cloud/botasaurus/docs/sign-up-tutorial/). 

This tutorial will walk you through signing up for 3 accounts on Omkar Cloud and give you a complete understanding of the process.
