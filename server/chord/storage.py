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

    def get(self, key):
        return self.storage[key]
    
    def set(self, key, value):
        self.storage[key] = value
        return None
    
    def remove(self, key):
        del self.storage[key]
        return None