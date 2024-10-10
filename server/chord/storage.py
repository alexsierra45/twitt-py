from abc import ABC


class Storage(ABC):
    def get(self, key) -> str:
        pass

    def set(self, key, value) -> bool:
        pass

    def remove(self, key) -> bool:
        pass

class RAMStorage(Storage):
    def __init__(self) -> None:
        self.storage = {}

    def get(self, key) -> str:
        return self.storage.get(key, '')
    
    def set(self, key, value) -> bool:
        self.storage[key] = value
        return True
    
    def remove(self, key) -> bool:
        del self.storage[key]
        return True