---
sidebar_position: 3.7
---
# Account Generator

Account Generator Module provides a convenient solution for creating accounts. It is particularly useful for automated tasks that require account creation in selenium.

## Usage

1. `generate_account(gender, country)`

Generates an account

**Arguments**

- `gender` (optional): The gender of the user account to generate. Value can be `Gender.MEN`, `Gender.WOMEN`, `Gender.BOTH`. Default's to `Gender.BOTH`
- `country` (optional): The country of the user account to generate. It accepts a value from the `Country` enum. The default value is `None`, which means the country can be any country.


**Example**

```python
from bose.account_generator import AccountGenerator, Gender, Country

account = AccountGenerator.generate_account(gender = Gender.WOMEN, country=Country.IN)
print(account)
```

**Output**

```json
{
    "name": "Vibha Almeida",
    "username": "vibhaalmeida@examplecom",
    "email": "vibha.almeida@gmail.com",
    "password": "letter16",
    "profile_picture": "https://randomuser.me/api/portraits/women/81.jpg",
    "phone": "9217029568",
    "address": "7492, Ratha Bheedi, Thanjavur, Tripura, India",
    "gender": "female",
    "country": "IN",
    "dob": {
        "date": "1992-07-29T22:51:53.073Z",
        "age": 30
    }
}
```

2. `generate_accounts(n, gender, country)`

Generates multiple user accounts.

**Arguments**

- `n`: The number of user accounts to generate.
- `gender` (optional): The gender of the user account to generate. Value can be `Gender.MEN`, `Gender.WOMEN`, `Gender.BOTH`. Default's to `Gender.BOTH`
- `country` (optional): The country of the user account to generate. It accepts a value from the `Country` enum. The default value is `None`, which means the country can be any country.


**Example**

```python
from bose.account_generator import AccountGenerator, Gender, Country

accounts = AccountGenerator.generate_accounts(3, gender = Gender.WOMEN, country=Country.IN)
print(accounts)
```

**Output**

```json
[
    {
        "name": "Sahana Nayak",
        "username": "sahananayak@examplecom",
        "email": "sahana.nayak@gmail.com",
        "password": "vietnam6",
        "profile_picture": "https://randomuser.me/api/portraits/women/35.jpg",
        "phone": "8679648937",
        "address": "424, Naiduthota, Khammam, Uttar Pradesh, India",
        "gender": "female",
        "country": "IN",
        "dob": {
            "date": "1997-10-03T07:38:31.090Z",
            "age": 25
        }
    },
    {
        "name": "Madhura Shroff",
        "username": "madhurashroff@examplecom",
        "email": "madhura.shroff@gmail.com",
        "password": "bettina1",
        "profile_picture": "https://randomuser.me/api/portraits/women/87.jpg",
        "phone": "8738692847",
        "address": "5106, Maharanipeta, Mehsana, Maharashtra, India",
        "gender": "female",
        "country": "IN",
        "dob": {
            "date": "1989-08-15T05:10:47.967Z",
            "age": 33
        }
    },
    {
        "name": "Hetal Kavser",
        "username": "hetalkavser@examplecom",
        "email": "hetal.kavser@gmail.com",
        "password": "django27",
        "profile_picture": "https://randomuser.me/api/portraits/women/94.jpg",
        "phone": "8033453360",
        "address": "5222, Colaba Causeway, Buxar, Daman and Diu, India",
        "gender": "female",
        "country": "IN",
        "dob": {
            "date": "1961-05-29T07:35:50.196Z",
            "age": 62
        }
    }
]
```
