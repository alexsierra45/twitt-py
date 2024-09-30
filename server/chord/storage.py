from abc import ABC
from typing import Dict, Tuple

class Data:
    def __init__(self, value: str, version: int, active: bool) -> None:
        self.value = value
        self.version = version
        self.active = active

class Storage(ABC):
    def get(self, key: str) -> Tuple[Data, bool]:
        pass

    def get_all(self) -> Tuple[Dict[str, Data], bool]:
        pass

    def get_remove_all(self) -> Tuple[Dict[str, Data], bool]:
        pass

    def set(self, key: str, value: Data) -> bool:
        pass

    def set_all(self, dict: Dict[str, Data]) -> bool:
        pass

    def remove(self, key) -> bool:
        pass

    def remove_all(self, dict: Dict[str, Data]) -> bool:
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