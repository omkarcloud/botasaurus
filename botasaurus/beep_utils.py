from os import name
from traceback import print_exc


if name == 'nt':
    import winsound

def play_beep():
    if name == 'nt':
        winsound.PlaySound("SystemQuestion", winsound.SND_ASYNC)
    else:
        print('\a')



def beep_input(prompt, should_beep=True):
    if should_beep:
        play_beep()
    
    try:
        user_input = input(prompt)
        return user_input
    except EOFError:
        print("Input stream closed unexpectedly.")
        # You can choose to return a default value or raise a custom exception here
        return None  # or raise CustomInputError("Input stream closed unexpectedly.")
    
def prompt( text="Press Enter To Continue...", should_beep = True):
        return beep_input(text, should_beep)
    
    # except Exception as e:
    #     print_exc()