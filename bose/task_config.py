

class TaskConfig:
    def __init__(self, target_website = 'target website' , log_time = True, prompt_to_close_browser=False, change_ip=False, beep=True, close_on_crash = False, output_filename='finished'):
        self.target_website = target_website
        self.log_time = log_time 
        self.prompt_to_close_browser = prompt_to_close_browser
        self.change_ip = change_ip
        self.beep = beep
        self.close_on_crash = close_on_crash
        self.output_filename = output_filename