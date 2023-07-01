---
sidebar_position: 20
---

# Temp Mail

The Temporary Email Module allows you to generate temporary email addresses on the fly, which is particularly useful when you need to confirm the email address of a bot account.

## Generating Temporary Mail

Here's an example of generating a temporary email address using a username.

```python
from bose.temp_mail import TempMail

username = "shyam"
link = TempMail.generate_email(username)

print(link)  # Prints "shyam@1secmail.com"
```

## Getting the Body of the Last Email

Here's an example of get the content (text or HTML) from the most recent email.

```python
from bose.temp_mail import TempMail

email = "shyam@1secmail.com"
body = TempMail.get_body(email)
print(body)
```

## Getting the Email Link

Here's an example of retrieving the first link in the most recent email. This is useful for obtaining the email verification link for sign-up emails.

```python
from bose.temp_mail import TempMail

email = "shyam@1secmail.com"
link = TempMail.get_email_link(email)
print(link)  # Prints "https://www.example.com/auth/sign-up-email-verify/a46091be2962410d90966ab0836e89da/"
```

## Deleting Emails

Here's an example of deleting all emails in a mailbox.

```python
from bose.temp_mail import TempMail

email = "shyam@1secmail.com"
TempMail.deleteMailbox(email)
```

## Getting the Email Link and Deleting the Mailbox

Here's an example of retrieving the first link in the most recent email and then deleting the emails.

```python
from bose.temp_mail import TempMail

email = "shyam@1secmail.com"
link = TempMail.get_email_link_and_delete_mailbox(email)
print("Link:", link)
```
