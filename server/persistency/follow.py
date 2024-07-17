import os
import grpc

from chord.node import ChordNode
from persistency.persistency import save, load, delete, file_exists
from interfaces.grpc.proto.models_pb2 import UserFollows

class FollowsPersitency:
    def __init__(self, node: ChordNode) -> None:
        self.node = node

    def load_following_list(self, username):
        path = os.path.join("User", username.lower(), "Follow")
        user_follows, err = load(self.node, path, UserFollows())

        if err == grpc.StatusCode.NOT_FOUND:
            return UserFollows(following_user_ids=[]), None

        if err:
            return None, grpc.StatusCode.INTERNAL("Failed to load following list: {}".format(err))

        return user_follows, None

    def add_to_following_list(self, username, other_username):
        path = os.path.join("User", username.lower(), "Follow")
        user_follows, err = self.load_following_list(username)

        if err:
            return False, err

        if other_username not in user_follows.following_user_ids:
            user_follows.following_user_ids.append(other_username)
            err = save(self.node, user_follows, path)

            if err:
                return False, grpc.StatusCode.INTERNAL("Failed to save following list: {}".format(err))

            return True, None

        return False, None

    def remove_from_following_list(self, username, other_username):
        path = os.path.join("User", username.lower(), "Follow")
        user_follows, err = self.load_following_list(username)

        if err:
            return False, err

        if other_username in user_follows.following_user_ids:
            user_follows.following_user_ids.remove(other_username)
            err = save(self.node, user_follows, path)

            if err:
                return False, grpc.StatusCode.INTERNAL("Failed to save following list: {}".format(err))

            return True, None

        return False, None
