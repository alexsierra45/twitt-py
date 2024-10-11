import os
import grpc

from chord.node import ChordNode
from persistency.persistency import save, load, delete, file_exists
from interfaces.grpc.models.models_pb2 import Post, UserPosts

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
        user_posts, err = load(self.node, path, UserPosts())
        list = []

        if not err:
            list = user_posts.posts_ids

        list.append(post_id)
        print(list)
        err = save(self.node, UserPosts(posts_ids = list), path)

        if err:
            return grpc.StatusCode.INTERNAL("Failed to save post to user: {}".format(err))

        return None

    def remove_from_posts_list(self, post_id, username):
        path = os.path.join("User", username.lower(), "Posts")
        posts, err = load(self.node, path, UserPosts())

        if err:
            return err

        list = [u for u in posts.posts_ids if u != post_id]
        err = save(self.node, UserPosts(posts_ids = list), path)

        if err:
            return grpc.StatusCode.INTERNAL("Failed to remove post from user: {}".format(err))

        return None

    def load_posts_list(self, username):
        path = os.path.join("User", username.lower(), "Posts")
        user_posts, err = load(self.node, path, UserPosts())
        print (user_posts)
        list = []

        if err == grpc.StatusCode.NOT_FOUND:
            return list, None

        if err:
            return None, grpc.StatusCode.INTERNAL("Failed to load user posts: {}".format(err))

        for post_id in user_posts.posts_ids:
            post, err = self.load_post(post_id)
            if err:
                return None, err
            list.append(post)
        return list, None
