from .base_data import BaseData

class WindowSize(BaseData):

    RANDOM = "RANDOM"
    HASHED = "HASHED"

    window_size_1920_1080 = [1920, 1080, ]
    window_size_1366_768 =  [1366, 768, ]
    window_size_1536_864 =  [1536, 864, ]
    window_size_1280_720 =  [1280, 720, ]
    window_size_1440_900 =  [1440, 900, ]
    window_size_1600_900 =  [1600, 900, ]

    def get_data(self):

        # Windows
        N_1920_1080 = 35
        N_1366_768 = 26
        N_1536_864 = 16
        N_1280_720 = 9
        N_1440_900 = 9
        N_1600_900 = 5
        _1920_1080 = [self.window_size_1920_1080] * N_1920_1080
        _1366_768 = [self.window_size_1366_768] * N_1366_768
        _1536_864 = [self.window_size_1536_864] * N_1536_864
        _1280_720 = [self.window_size_1280_720] * N_1280_720
        _1440_900 = [self.window_size_1440_900] * N_1440_900
        _1600_900 = [self.window_size_1600_900] * N_1600_900

        result = _1920_1080 + _1366_768 + _1536_864 + _1280_720 + _1440_900 + _1600_900
        return result
    
    def window_size_to_string(window_size):
        w, h = window_size 
        return f'{w},{h}'

WindowSizeInstance = WindowSize() 
