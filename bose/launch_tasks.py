from .local_storage import LocalStorage
from .output import Output
from .utils import sleep_for_n_seconds
from .ip_utils import get_valid_ip
from .beep_utils import beep_input

def prompt_change_ip(should_beep):
    current_ip = get_valid_ip()
    seen_ips =  LocalStorage.get_item("seen_ips", [])
    
    next_prompt = "Please change your IP and press Enter to continue..."
    
    while True:
        beep_input(next_prompt, should_beep)
        new_ip = get_valid_ip()

        if new_ip == current_ip:
            next_prompt = """In order to proceed, it is necessary to change your IP address as a precautionary measure against Bot Detection. Please visit TODO_LINK to learn how to change your IP. Once you have successfully changed your IP address, please press Enter to continue..."""

        elif new_ip in seen_ips:
            next_prompt = "Your computer previously had this IP address. Please change your IP and press Enter to continue..."
        else:
            LocalStorage.set_item("seen_ips", LocalStorage.get_item("seen_ips", []) + [current_ip])
            return new_ip

def launch_tasks(*tasks):
    for Task in tasks: 
        print('Task Started')

        task  = Task()
        task_config = task.get_task_config()

        should_first_beep = len(tasks) > 1

        if task_config.prompt_to_close_browser: 
            prompt_message = f"Kindly close other browsers where {task_config.target_website} is open to prevent detection from {task_config.target_website} and press enter to continue..."
            beep_input(prompt_message, task_config.beep and should_first_beep)

        if task_config.change_ip: 
            prompt_change_ip(task_config.beep and should_first_beep)

        data = task.get_data()
        
        if type(data) is not list:
            data = [data]
        
        schedules = task.schedule(data)

        output = []
        for index in range(len(data)):
            current_data = data[index]
            delay = schedules[index]['delay']

            current_output = task.begin_task(current_data, task_config)
            
            if type(current_output) is dict:
                current_output = [current_output]

            if type(current_output) is list:
                output = output + current_output

            if len(output) > 0: 
                Output.write_json(output, task_config.output_filename)

            if task_config.change_ip: 
                prompt_change_ip(task_config.beep)


            if delay > 0:
                is_last = index == len(data) -1
                if is_last:
                    pass
                else:
                    sleep_for_n_seconds(delay)

        print('Task Completed!')

        if len(output) > 0: 
            Output.write_json(output, task_config.output_filename)
            Output.write_csv(output, task_config.output_filename)