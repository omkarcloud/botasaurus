import os

if os.name == 'nt':
    import winsound

def play_beep():
    if os.name == 'nt':
        winsound.PlaySound("SystemQuestion", winsound.SND_ASYNC)
    else:
        print('\a')


def beep_input(prompt, should_beep = True):
    if should_beep:
        play_beep()
    return input(prompt)

