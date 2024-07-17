import os
import grpc

from chord.node import ChordNode
from persistency.persistency import save, load, delete, file_exists
from interfaces.grpc.proto.models_pb2 import Post, UserPosts

class PostPersitency:
    def __init__(self, node: ChordNode) -> None:
        self.node = node

    def load_post(self, post_id):
        path = os.path.join("Post", post_id)
        post, err = load(self.node, path, Post())

        if err == grpc.StatusCode.NOT_FOUND:
            return None, grpc.StatusCode.NOT_FOUND
        elif err:
            return None, grpc.StatusCode.INTERNAL

        return post, None

    def remove_post(self, post_id):
        path = os.path.join("Post", post_id)
        err = delete(self.node, path)

        if err:
            return grpc.StatusCode.INTERNAL("Failed to remove post: {}".format(err))

        return None

    def save_post(self, post):
        path = os.path.join("Post", post.post_id)
        err = save(self.node, post, path)

        if err:
            return grpc.StatusCode.INTERNAL("Failed to save post: {}".format(err))

        return None

    def add_to_posts_list(self, post_id, username):
        path = os.path.join("User", username.lower(), "Posts")
        posts, err = self.load_posts_list(username)

        if err:
            return err

        posts.posts_ids.append(post_id)
        err = save(self.node, posts, path)

        if err:
            return grpc.StatusCode.INTERNAL("Failed to save post to user: {}".format(err))

        return None

    def remove_from_posts_list(self, post_id, username):
        path = os.path.join("User", username.lower(), "Posts")
        posts, err = self.load_posts_list(username)

        if err:
            return err

        posts.posts_ids = [u for u in posts.posts_ids if u != post_id]
        err = save(self.node, posts, path)

        if err:
            return grpc.StatusCode.INTERNAL("Failed to remove post from user: {}".format(err))

        return None

    def load_posts_list(self, username):
        path = os.path.join("User", username.lower(), "Posts")
        user_posts, err = load(self.node, path, UserPosts())

        if err == grpc.StatusCode.NOT_FOUND:
            return UserPosts(posts_ids=[]), None

        if err:
            return None, grpc.StatusCode.INTERNAL("Failed to load user posts: {}".format(err))

        return user_posts, None
