class DontCache:
    def __init__(self, result):
        self.data = result

def is_dont_cache(obj):
    return isinstance(obj, DontCache)