import grpc

from server.chord.storage import RAMStorage

class ChordNode:
    def __init__(self):
        self.storage = RAMStorage()

    def set_key(self, key, value):
        self.storage.set(key, value)
        return None

    def get_key(self, key):
        try: 
            return self.storage.get(key), None
        except:
            return None, grpc.StatusCode.NOT_FOUND

    def remove_key(self, key):
        try:
            del self.storage.remove(key)
            return None
        except:
            return grpc.StatusCode.NOT_FOUND