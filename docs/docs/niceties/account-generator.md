---
sidebar_position: 10
---

# Account Generator

When you are creating bot accounts, you want them to look like real humans.

To achieve this, we have developed an Account Generator module that can generate names, emails, profile pictures, passwords, and more, making the accounts appear more human.

With this module, your bots will seem more human than actual humans. Seriously!

## Generating a Single Account

Here's an example of how to create an Indian account:

```python
from bose.account_generator import AccountGenerator, Gender, Country

account = AccountGenerator.generate_account(country=Country.IN)
print(account)
```

**Output**

```json
{
    "id": 1,
    "name": "Akshatha Tipparti",
    "username": "akshathatipparti1967",
    "email": "akshathatipparti1967@1secmail.net",
    "password": "manutdI@6",
    "uuid": "0f989e05-3433-4bad-9b91-7f6b810320aa",
    "profile_picture": "https://randomuser.me/api/portraits/women/52.jpg",
    "phone": "7021066754",
    "address": "5824, Somwar Peth, Aizawl, Gujarat, India",
    "gender": "female",
    "country": "IN",
    "dob": {
        "year": 1967,
        "month": 6,
        "day": 8,
        "date": "1967-06-08T12:21:59.255Z",
        "age": 56
    }
}
```

## Generating Multiple Accounts

To generate multiple accounts, you can use the `generate_accounts` function and specify the number of accounts to create.

Here's an example of how to create 3 Indian accounts:

```python
from bose.account_generator import AccountGenerator, Gender, Country

accounts = AccountGenerator.generate_accounts(3, country=Country.IN)
print(accounts)
```

**Output**

```json
[
    {
        "id": 1,
        "name": "Ekansh Chiplunkar",
        "username": "ekanshchiplunkar1955",
        "email": "ekanshchiplunkar1955@icznn.com",
        "password": "medusaK;9",
        "uuid": "53be00f6-3545-447b-89a0-83bedae4131e",
        "profile_picture": "https://randomuser.me/api/portraits/men/88.jpg",
        "phone": "9692011812",
        "address": "9239, Altamount Rd, Akola, Uttarakhand, India",
        "gender": "male",
        "country": "IN",
        "dob": {
            "year": 1955,
            "month": 11,
            "day": 19,
            "date": "1955-11-19T03:21:54.574Z",
            "age": 67
        }
    },
    {
        "id": 2,
        "name": "Navami Banerjee",
        "username": "navamibanerjee1988",
        "email": "navamibanerjee1988@1secmail.net",
        "password": "thegame4(F",
        "uuid": "509f7a1f-ba01-46a1-8569-1044d719193c",
        "profile_picture": "https://randomuser.me/api/portraits/women/2.jpg",
        "

phone": "7383195258",
        "address": "5800, Commercial St, Rourkela, Dadra and Nagar Haveli, India",
        "gender": "female",
        "country": "IN",
        "dob": {
            "year": 1988,
            "month": 9,
            "day": 6,
            "date": "1988-09-06T20:12:42.910Z",
            "age": 34
        }
    },
    {
        "id": 3,
        "name": "Ajay Singh",
        "username": "ajaysingh1953",
        "email": "ajaysingh1953@ezztt.com",
        "password": "420247-nW",
        "uuid": "fe3c5fbe-e9c5-4cb0-b5d5-2f838e4a6674",
        "profile_picture": "https://randomuser.me/api/portraits/men/39.jpg",
        "phone": "7821929055",
        "address": "661, Old Jail Rd, Arrah, Gujarat, India",
        "gender": "male",
        "country": "IN",
        "dob": {
            "year": 1953,
            "month": 2,
            "day": 24,
            "date": "1953-02-24T16:32:41.904Z",
            "age": 70
        }
    }
]
```