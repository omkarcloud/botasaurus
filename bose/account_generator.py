import string
import requests
import random
from .temp_mail import TempMail
from .utils import merge_list_of_dicts, merge_dicts_in_one_dict

from datetime import datetime

def convert_timestamp(timestamp):
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    year = dt.year
    month = dt.month
    day = dt.day
    return {"year": year, "month": month, "day": day}


class Gender():
    MEN = 'male'
    BOTH = ''
    WOMEN = 'female'

class Country():
    AU = 'AU'
    BR = 'BR'
    CA = 'CA'
    CH = 'CH'
    DE = 'DE'
    DK = 'DK'
    ES = 'ES'
    FI = 'FI'
    FR = 'FR'
    GB = 'GB'
    IE = 'IE'
    IN = 'IN'
    IR = 'IR'
    MX = 'MX'
    NL = 'NL'
    NO = 'NO'
    NZ = 'NZ'
    RS = 'RS'
    TR = 'TR'
    UA = 'UA'
    US = 'US'
class ProblemWithGetPersonData(Exception):
    """Problem with obtaining personal data"""


def get_missing_chars(word:str):
    missing_chars = []
    
    if not any(char.isupper() for char in word):
        missing_chars.append(random.choice(string.ascii_uppercase))
    
    if not any(char.islower() for char in word):
        missing_chars.append(random.choice(string.ascii_lowercase))
    
    if not any(char.isdigit() for char in word):
        missing_chars.append(random.choice(string.digits))
    
    if not any(char in string.punctuation for char in word):
        missing_chars.append(random.choice(string.punctuation))
    
    random.shuffle(missing_chars)
    return ''.join(missing_chars)

def process_password(word):
    word = word + get_missing_chars(word)

    if len(word) < 8:
        digits_needed = 8 - len(word)
        
        # Generate a random number with the required number of digits
        random_number = random.randint(10 ** (digits_needed - 1), (10 ** digits_needed) - 1)
        
        # Convert the number to a string and append it to the word
        word = word + str(random_number)


    return word

def __get_person(user_data: dict):
    email = user_data["email"]
    
    dob = convert_timestamp(user_data["dob"]["date"])

    username = user_data["email"].replace("@example.com" , "").replace(".", "") + str(dob['year'])
    
    email = TempMail.generate_email(username)

    address = str(user_data["location"]["street"]["number"]) + ", " + user_data["location"]["street"]["name"] + ", " + user_data["location"]["city"] + ", " +user_data["location"]["state"] +  ", " + user_data["location"]["country"] 

    
    return {
     "name": user_data["name"]["first"] + " " + user_data["name"]["last"], 
     "first_name": user_data["name"]["first"],
     "last_name": user_data["name"]["last"],
     "username": username, 
     "email": email,
     "password":process_password(user_data["login"]["password"]),
     "uuid": user_data["login"]["uuid"], 
     "profile_picture" : user_data["picture"]["large"], 
     "phone" : user_data["phone"],
     "address" : address,
     "gender":user_data["gender"],    
     "country": user_data["nat"],
     "dob" : merge_dicts_in_one_dict(dob, user_data["dob"]) , 
    #  "created_at" : datetime_to_str(datetime.now())
    }



def generate_persons(count: int, gender: Gender = Gender.BOTH, country: Country = None):

    if not isinstance(count, int) or count < 1:
        count = 1

    params = {'gender': gender, 'results': count}
    if country is not None:
         params['nat'] = country
    
    r = requests.get('https://randomuser.me/api', params=params)
    if r.status_code != 200:
        raise ProblemWithGetPersonData()

    results = r.json()['results']

    final = [__get_person(data) for data in results]

    ids =  [{"id":  1 + i } for i in range(len(results))]
    
    datas = merge_list_of_dicts(  ids, final)
    
    return datas



class AccountGenerator:
    def generate_account(gender: Gender = Gender.BOTH, country: Country = None):
            return generate_persons(1, gender, country)[0]

    def generate_accounts(n, gender: Gender = Gender.BOTH, country: Country = None):
            return generate_persons(n, gender, country)
