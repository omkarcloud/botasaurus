
from os import name

def play_beep():
    if name == 'nt':
        import winsound
        winsound.PlaySound("SystemQuestion", winsound.SND_ASYNC)
    else:
        print('\a')

_is_multiprocessing = None

def is_multiprocessing():
    global _is_multiprocessing
    if _is_multiprocessing is None:
        import multiprocessing
        try:
            _is_multiprocessing = multiprocessing.current_process().name != 'MainProcess'
        except AttributeError:
            _is_multiprocessing = False
    return _is_multiprocessing

def beep_input(prompt, should_beep=True):
    if should_beep:
        play_beep()
    if is_multiprocessing():
            print(prompt)
            print("Prompting is disabled in multiprocessing mode. Therefore Returning None.")
            return None
    else:
        try:
            user_input = input(prompt)
            return user_input
        except EOFError:
            print("Input stream closed unexpectedly.")
            # You can choose to return a default value or raise a custom exception here
            return None  # or raise CustomInputError("Input stream closed unexpectedly.")
    
def prompt( text="Press Enter To Continue...", should_beep = True):
        return beep_input(text, should_beep)
    