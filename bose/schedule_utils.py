from .utils import merge_list_of_dicts, merge_dicts_in_one_dict
import random

def generate_random_number(from_num, to_num=None):
    if to_num is None:
        return from_num
    return random.randint(from_num, to_num)

class ScheduleUtils:
    def delay(tasks, from_seconds = 30, to_seconds = None):
        delays = [ {"delay":  generate_random_number(from_seconds, to_seconds) } for i in range(len(tasks))]
        
        # result = merge_list_of_dicts(tasks, delays)
        return delays

    def delay_5s(tasks):
        return ScheduleUtils.delay(tasks, 5)


    def no_delay(tasks):
        return ScheduleUtils.delay(tasks, 0)

    def delay_30s_to_60s(tasks):
        return ScheduleUtils.delay(tasks, 30, 60)


    def delay_30m_to_60m(tasks):
        return ScheduleUtils.delay(tasks, 30 * 60, 60 * 60)

    