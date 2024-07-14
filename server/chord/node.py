import grpc

class ChordNode:
    def __init__(self):
        self.storage = {}

    def set_key(self, key, value):
        self.storage[key] = value
        return None

    def get_key(self, key):
        if key in self.storage:
            return self.storage[key], None
        else:
            return None, grpc.StatusCode.NOT_FOUND

    def remove_key(self, key):
        if key in self.storage:
            del self.storage[key]
            return None
        else:
            return grpc.StatusCode.NOT_FOUND