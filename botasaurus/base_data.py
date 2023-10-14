from itertools import cycle
import random
import copy

def copy_list(original_list):
    """
    Returns a deep copy of a list containing dictionaries or strings.

    Args:
    original_list (list): The list to copy.

    Returns:
    list: A deep copy of the original list.
    """
    return copy.deepcopy(original_list)


def delete_from_list(list_of_dicts, dict_item):
    for i in range(len(list_of_dicts)):
        if dict_item in list_of_dicts:
            list_of_dicts.remove(dict_item)
    return list_of_dicts

# see https://stackoverflow.com/questions/27522626/hash-function-in-python-3-3-returns-different-results-between-sessions
def myHash(text:str):
  hash=0
  for ch in text:
    hash = ( hash*281  ^ ord(ch)*997) & 0xFFFFFFFF
  return hash

class BaseData():
    def get_data(self):
        pass
    
    
    @property
    def has_items(self):
        return len(self.data) > 0

    def __init__(self):
        self.has_initialized  = True
        data = self.get_data()
        # random.shuffle(data)
        self.set_data(data)

    def set_data(self, data):
        self.data = data
        copied_list = copy_list(self.data)
        random.shuffle(copied_list)
        self.cycled_data = cycle(copied_list)

    def get_random_cycled(self):
        if self.has_items:
            return next(self.cycled_data)

    def get_random(self):
        return random.choice(self.data)

    def remove_data(self, item):
        self.set_data(delete_from_list(self.data, item))

    def get_hashed(self, value):
        ls   = self.data
        ls_len = len(ls)
        hashed_value = myHash(value if value is not None else '_')
        return ls[hashed_value % ls_len]

    def get_n(self, n):
        ls = []
        for i in range(n):
            ls.append(self.get_random_cycled())
        return ls

    def get_hundred(self):
        return self.get_n(100)


if __name__ == "__main__":
        
    class Test(BaseData):
        def get_data(self):
            if False:
            # if IS_PRODUCTION:
                N_US = 0
                N_GB = 0
                N_FR = 0
                N_NL = 100
                N_NO = 0
                N_CA = 0
                N_IN = 0
                # N_US = 50
                # N_GB = 10
                # N_FR = 10
                # N_NL = 10
                # N_NO = 10
                # N_CA = 10
                # N_IN = 0
            else:
                N_US = 1
                N_GB = 1
                N_FR = 1
                N_NL = 1
                N_NO = 1
                N_CA = 1
                N_IN = 1

            US = [{"country_code": "US"}] * N_US
            GB = [{"country_code": "GB"}] * N_GB
            FR = [{"country_code": "FR"}] * N_FR
            NL = [{"country_code": "NL"}] * N_NL
            NO = [{"country_code": "NO"}] * N_NO
            CA = [{"country_code": "CA"}] * N_CA
            IN = [{"country_code": "IN"}] * N_IN

            result = US+GB+FR+NL+NO+CA+IN
            return result


    TestInstance = Test() 
    print(TestInstance.data)
    TestInstance.remove_data(TestInstance.get_random_cycled())
    TestInstance.remove_data(TestInstance.get_random_cycled())
    TestInstance.remove_data(TestInstance.get_random_cycled())
    TestInstance.remove_data(TestInstance.get_random_cycled())
    TestInstance.remove_data(TestInstance.get_random_cycled())
    TestInstance.remove_data(TestInstance.get_random_cycled())
    TestInstance.remove_data(TestInstance.get_random_cycled())
    print(TestInstance.data)
