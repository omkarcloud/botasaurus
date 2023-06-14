from account_generator_helper import generate_person, generate_persons



phone = ReceiveSms()

country = phone.get_country(Counties.UNITED_STATES)
phone = country.get_number()
print('Phone number :', phone.number)  # Phone number : 380665327743

for message in phone.get_last_messages():
    print(message)  # (Message ...)
