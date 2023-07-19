from datetime import datetime
from .ip_utils import find_ip_details
from .utils import pretty_format_time


def format_time_diff(start_time_datetime, end_time_datetime):
    time_diff = end_time_datetime - start_time_datetime
    total_seconds = int(time_diff.total_seconds())

    minutes, seconds = divmod(total_seconds, 60)

    # Format the time difference as a string
    time_str = ""
    if minutes > 0:
        time_str += f"{minutes} {'minutes' if minutes > 1 else 'minute'}"
    if seconds >= 0:
        if time_str:
            time_str += " "
        time_str += f"{seconds} {'seconds' if seconds > 1 else 'second'}"

    return time_str

def copy_and_remove_keys(input_dict):
    # Make a shallow copy of the input dictionary
    new_dict = input_dict.copy()

    # Remove the specified keys if they exist in the dictionary
    keys_to_remove = ['end_time_datetime', 'start_time_datetime']
    for key in keys_to_remove:
        new_dict.pop(key, None)

    return new_dict

class TaskInfo():
  data = {}
  
  def start(self):
    self.data["start_time_datetime"] = datetime.now()
    pass
  
  def get_data(self):
     return copy_and_remove_keys(self.data)
  
  def end(self):
    self.data["end_time_datetime"] = datetime.now()
    self.data["duration"] = format_time_diff(self.data["start_time_datetime"],self.data["end_time_datetime"])
    

    self.data["start_time"] = pretty_format_time(self.data["start_time_datetime"])
    self.data["end_time"] = pretty_format_time(self.data["end_time_datetime"])


  def set_ip(self):
    self.data["ip_details"] = find_ip_details()

  def set_task_name(self, task_name):
    self.data["task_name"] = task_name


if __name__ == "__main__":
    t = TaskInfo()
    t.start()
    t.end()
    t.end()
    t.set_ip()
    print(t.get_data())