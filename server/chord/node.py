import grpc

from server.chord.storage import RAMStorage

class ChordNode:
    def __init__(self):
        self.storage = RAMStorage()

    def set_key(self, key, value):
        return self.storage.set(key, value)

    def get_key(self, key):
        return self.storage.get(key)

    def remove_key(self, key):
        return self.storage.remove(key)