---
sidebar_position: 70
---

# Profile

The Profile module is used to store key-value pairs about the current profile. 

The most common use case for Profile is to store account details after the bot has created an account on the target website. For example:

```python 

account = AccountGenerator.generate_account()
Profile.set_profile(account)

```

Above Code will store the current account details in `profile.json` as follows:

```json
{
    "shivanshsullad1980": {
        "id": 1,
        "name": "Shivansh Sullad",
        "username": "shivanshsullad1980",
        "email": "shivanshsullad1980@wuuvo.com",
        "password": "shelby*6B",
        "uuid": "de000c29-6e64-4298-9c4c-ca94019b2ba6",
        "profile_picture": "https://randomuser.me/api/portraits/men/28.jpg",
        "phone": "7057166416",
        "address": "318, Bannerghatta Rd, Purnia, Bihar, India",
        "gender": "male",
        "country": "IN",
        "dob": {
            "year": 1980,
            "month": 5,
            "day": 26,
            "date": "1980-05-26T14:53:53.510Z",
            "age": 43
        },
        "created_at": "2023-06-29 17:25:08",
        "updated_at": "2023-06-29 17:25:08"
    }
}
```

---

Here are example demonstrating some additional methods available in the Profile module:


```python
from bose import Profile
# Set an item in the current profile
Profile.set_item('username', 'johndoe')

# Retrieve an item from the current profile
username = Profile.get_item('username')

# Remove an item from the current profile
Profile.remove_item('username')

# Clear all items from the current profile
Profile.clear()
```

----

Another common use case is to retrieve a list of all created profiles. The following example demonstrates how to achieve that:

```python
from bose import Profile

print(Profile.get_profiles())
```

--- 

If you only want to store the name, email, and password in the Profile, you can do it like this:

```python
from bose import Profile

account = AccountGenerator.generate_account()

Profile.set_item('name', account['name'])
Profile.set_item('email', account['email'])
Profile.set_item('password', account['password'])
```
