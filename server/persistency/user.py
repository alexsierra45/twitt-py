import os
import grpc

from chord.node import ChordNode
from persistency.persistency import save, load, file_exists
from interfaces.grpc.models.models_pb2 import User

class UserPersitency:
    def __init__(self, node: ChordNode) -> None:
        self.node = node

    def exists_user(self, username):
        path = os.path.join("User", username.lower())
        return file_exists(self.node, path)

    def load_user(self, username):
        path = os.path.join("User", username.lower())
        user, err = load(self.node, path, User())

        if err == grpc.StatusCode.NOT_FOUND:
            return None, grpc.StatusCode.NOT_FOUND
        elif err:
            return None, grpc.StatusCode.INTERNAL

        return user, None

    def save_user(self, user):
        path = os.path.join("User", user.username.lower())
        err = save(self.node, user, path)

        if err:
            return grpc.StatusCode.INTERNAL

        return None