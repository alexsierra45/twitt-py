from abc import ABC


class Storage(ABC):
    def get(self, key):
        pass

    def set(self, key, value):
        pass

    def remove(self, key):
        pass

class RAMStorage(Storage):
    def __init__(self) -> None:
        self.storage = {}

    def get(self, key: str):
        try:
            value = self.storage[key]
            return value, None
        except Exception as e:
            return None, e
    
    def set(self, key: str, value: str):
        try:
            self.storage[key] = value
            return None
        except Exception as e:
            return e
    
    def remove(self, key: str):
        try:
            del self.storage[key]
            return None
        except Exception as e:
            return e