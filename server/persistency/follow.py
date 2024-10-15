import os
import grpc

from chord.node import ChordNode
from persistency.persistency import save, load, delete, file_exists
from persistency.user import UserPersitency
from interfaces.grpc.models.models_pb2 import UserFollows

class FollowsPersitency:
    def __init__(self, node: ChordNode) -> None:
        self.node = node

    def load_following_list(self, username):
        path = os.path.join("User", username.lower(), "Follow")
        user_follows, err = load(self.node, path, UserFollows())
        list = []
        if err == grpc.StatusCode.NOT_FOUND:
            return list, None

        if err:
            return None, grpc.StatusCode.INTERNAL("Failed to load following list: {}".format(err))

        for user_id in user_follows.following_user_ids:
            # user, err = UserPersitency().load_user(user_id)
            # if err:
            #     return None, err
            list.append(user_id)
        return list, None

    def add_to_following_list(self, username, other_username):
        path = os.path.join("User", username.lower(), "Follow")
        user_follows, err = self.load_following_list(username)
        list = []
        if not err:
            list = user_follows

        if other_username not in list:
            list.append(other_username)
            err = save(self.node, UserFollows(following_user_ids = list), path)

            if err:
                return False, grpc.StatusCode.INTERNAL("Failed to save following list: {}".format(err))

            return True, None

        return False, None

    def remove_from_following_list(self, username, other_username):
        path = os.path.join("User", username.lower(), "Follow")
        user_follows, err = self.load_following_list(username)

        list = []


        if not err:
            list = user_follows

        if other_username in list:
            list.remove(other_username)
            err = save(self.node, UserFollows(following_user_ids = list), path)

            if err:
                return False, grpc.StatusCode.INTERNAL("Failed to save following list: {}".format(err))

            return True, None

        return False, None
