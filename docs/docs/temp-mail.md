---
sidebar_position: 3.5
---
# Temp Mail

Temporary Email Module offers a convenient solution for receiving temporary emails. It is particularly useful for automated tasks that require email verification during account creation.

## Usage

1. `get_domains`

Returns a list of available domain options for generating temporary email addresses.

```python
from bose.temp_mail import TempMail

domains = TempMail.get_domains()
print(domains) # prints ['1secmail.com', '1secmail.org', '1secmail.net', 'kzccv.com', 'qiott.com', 'wuuvo.com', 'icznn.com', 'ezztt.com']
```

2. `get_email_link(email)`

Get's the first link from the most recent email message received in the given email address.


```python
from bose.temp_mail import TempMail

email = "shyam@1secmail.com"
link = TempMail.get_email_link(email)
print(link) 
```

3. `get_body(email)`

Get's the content (text or HTML) from the most recent email message received in the given email address.


```python
from bose.temp_mail import TempMail

email = "shyam@1secmail.com"
body = TempMail.get_body(email)
print(body) 
```


4. `deleteMailbox(email)`

Deletes the mailbox associated with the provided email address. 


```python
from bose.temp_mail import TempMail

email = "shyam@1secmail.com"
TempMail.deleteMailbox(email)
```

5. `get_email_link_and_delete_mailbox(email)`

Combines the functionality of `get_email_link` and `deleteMailbox(email)`. It first retrieves the first link from the most recent email and then deletes the mailbox, returning the link.


```python
from bose.temp_mail import TempMail

email = "shyam@1secmail.com"
link = TempMail.get_email_link_and_delete_mailbox(email)
print("Link:", link)
```
