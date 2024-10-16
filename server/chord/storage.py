import threading
from typing import Dict, Tuple

class Data:
    def __init__(self, value: str, version: int, active: bool = True) -> None:
        self.value = value
        self.version = version
        self.active = active

    def is_empty(self) -> bool:
        return self.value == ''
    
    def __str__(self) -> str:
        return f'{self.value},{self.version},{self.active}'
    
    def __repr__(self) -> str:
        return f'Data(value={self.value}, version={self.version}, active={self.active})'
    
class DefaultData(Data):
    def __init__(self) -> None:
        super().__init__('', 0)

class Storage:
    def __init__(self) -> None:
        self.storage_lock = threading.RLock()
        self.storage = None
        
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

    def remove(self, key, time, rep: bool = True) -> bool:
        pass

    def remove_all(self, dict: Dict[str, int]) -> bool:
        pass

class RAMStorage(Storage):
    def __init__(self) -> None:
        super().__init__()
        self.storage: Dict[str, Data] = {}

    def get(self, key) -> Tuple[Data, bool]:
        data = self.storage.get(key, DefaultData())
        return data, data.is_empty()
    
    def set(self, key: str, data: Data) -> bool:
        data.active = True
        self.storage[key] = data
        return True
    
    def remove(self, key: str, time: int, rep: bool = True) -> bool:
        data = self.storage[key]
        if rep:
            data.active = False
        data.version = time
        self.storage[key] = data
        return True
    
    def get_all(self) -> Tuple[Dict[str, Data], bool]:
        new_storage: Dict[str, Data] = {}
        for key, data in self.storage.items():
            if data.active:
                new_storage[key] = data

        return new_storage, True
    
    def get_remove_all(self) -> Tuple[Dict[str, Data], bool]:
        new_storage: Dict[str, Data] = {}
        for key, data in self.storage.items():
            if not data.active:
                new_storage[key] = data

        return new_storage, True
    
    def set_all(self, dict: Dict[str, Data]) -> bool:
        for key, data in dict.items():
            data.active = True
            self.storage[key] = data

        return True
    
    def remove_all(self, dict: Dict[str, int]) -> bool:
        for key, version in dict.items():
            data = self.storage[key]
            data.active = False
            data.version = version
            self.storage[key] = data

        return True