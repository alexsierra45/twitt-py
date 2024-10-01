from typing import Generic, List, TypeVar

T = TypeVar('T')

class DynamicList(Generic[T]):
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.list: List[T] = []

    def get_index(self, index: int) -> T:
        try:
            return self.list[index]
        except:
            return None

    def set_index(self, index: int, value: T):
        new_list = self.list[:index] + [value] + self.list[index:]

        if len(new_list) > self.capacity:
            new_list = new_list[:self.capacity]

        self.list = new_list

    def remove_index(self, index: int):
        self.list = self.list[:index] + self.list[index + 1:]

    def __len__(self) -> int:
        return len(self.list)

    def clear(self):
        self.list = []