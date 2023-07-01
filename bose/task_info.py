import requests
from datetime import datetime
import traceback

from .ip_utils import find_ip_details

from .utils import pretty_format_time


def format_time_diff(start_time, end_time):
    time_diff = end_time - start_time
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


class TaskInfo():
  data = {}
  
  def start(self):
    self.data["start_time"] = datetime.now()
    pass
  
  
  def end(self):
    self.data["end_time"] = datetime.now()
    self.data["duration"] = format_time_diff(self.data["start_time"],self.data["end_time"])
    

    self.data["start_time"] = pretty_format_time(self.data["start_time"])
    self.data["end_time"] = pretty_format_time(self.data["end_time"])


  def set_ip(self):
    self.data["ip_details"] = find_ip_details()

  def set_task_name(self, task_name):
    self.data["task_name"] = task_name


if __name__ == "__main__":
    t = TaskInfo()
    t.start()
    t.end()
    t.set_ip()
    print(t.data)