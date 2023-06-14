import requests
import enum
import random

from .temp_mail import TempMail

# from greatawesomeutils.lang import *

class Gender(enum.Enum):
    MEN = 'male'
    BOTH = ''
    WOMEN = 'female'

class Country(enum.Enum):
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


def process_password(word):
    if not any(char.isdigit() for char in word):
        # Append '1' to the word if no number is found
        word += str(random.randint(10 ** (1 - 1), (10 ** 1) - 1))

    if len(word) < 8:
        digits_needed = 8 - len(word)
        
        # Generate a random number with the required number of digits
        random_number = random.randint(10 ** (digits_needed - 1), (10 ** digits_needed) - 1)
        
        # Convert the number to a string and append it to the word
        word = word + str(random_number)


    return word

def __get_person(user_data: dict):
    email = user_data["email"]
    
    
    username = user_data["email"].replace("@example.com" , "").replace(".", "")
    
    email_username = user_data["email"].replace("@example.com" , "")
    email = TempMail.generate_email(email_username)

    address = str(user_data["location"]["street"]["number"]) + ", " + user_data["location"]["street"]["name"] + ", " + user_data["location"]["city"] + ", " +user_data["location"]["state"] +  ", " + user_data["location"]["country"] 

    return {
     "name": user_data["name"]["first"] + " " + user_data["name"]["last"], 
     "username": username, 
     "email": email,
     "password":process_password(user_data["login"]["password"]),
     "profile_picture" : user_data["picture"]["large"], 
     "phone" : user_data["phone"],
     "address" : address,
     "gender":user_data["gender"],    
     "country": user_data["nat"],
     "dob" : user_data["dob"]
    }



def generate_persons(count: int, gender: Gender = Gender.BOTH, country: Country = None):

    if not isinstance(count, int) or count < 1:
        count = 1

    params = {'gender': gender.value, 'results': count}
    if country is not None:
         params['nat'] = country.value
    
    r = requests.get('https://randomuser.me/api', params=params)
    if r.status_code != 200:
        raise ProblemWithGetPersonData()

    return [__get_person(data) for data in r.json()['results']]



class AccountGenerator:
    def generate_account(gender: Gender = Gender.BOTH, country: Country = None):
            return generate_persons(1, gender, country)[0]

    def generate_accounts(n, gender: Gender = Gender.BOTH, country: Country = None):
            return generate_persons(n, gender, country)

if __name__ == '__main__':
    account = AccountGenerator.generate_accounts(3, gender = Gender.WOMEN, country=Country.IN)
    # write_temp_json(account)
    # print(account)