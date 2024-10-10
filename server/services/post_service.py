import logging
import grpc
from concurrent import futures
import time
import re

from numpy import iterable
from config import RSA_PUBLIC_KEY_PATH
from services.interceptors import AuthInterceptor, StreamLoggingInterceptor, UnaryLoggingInterceptor
from interfaces.grpc.proto.posts_pb2 import GetPostResponse, CreatePostResponse, RepostResponse, DeletePostResponse, GetUserPostsResponse
from interfaces.grpc.proto.posts_pb2_grpc import PostServiceServicer, add_PostServiceServicer_to_server
from interfaces.grpc.models.models_pb2 import Post

class PostService(PostServiceServicer):
    def __init__(self, user_persistency, post_persistency):
        self.post_persistency = post_persistency
        self.user_persistency = user_persistency

    def GetPost(self, request, context):
        post_id = request.post_id
        post, err = self.post_persistency.load_post(post_id)

        if err:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

        return GetPostResponse(post=post)

    def CreatePost(self, request, context):
        user_id = request.user_id
        # if not self._check_permission(context, user_id):
        #     context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission denied")

        content = request.content
        if len(content) > 140:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Post content is too long")
        if len(content) == 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Posts must have content")

        post_id = str(time.time_ns())
        post = Post(post_id = post_id, user_id = user_id, content = content, timestamp = int(time.time()))

        err = self.post_persistency.save_post(post)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to save post")

        err = self.post_persistency.add_to_posts_list(post_id, user_id)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to add post to user list")

        return CreatePostResponse(post=post)

    def Repost(self, request, context):
        user_id = request.user_id
        # if not self._check_permission(context, user_id):
        #     context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission denied")
        posts, err = self.post_persistency.load_posts_list(user_id)

        for post in posts:
            if post.original_post_id == request.original_post_id:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "User already reposted this post")

        original_post, err = self.post_persistency.load_post(request.original_post_id)
        if err:
            context.abort(grpc.StatusCode.NOT_FOUND, "Original post not found")

        post_id = str(time.time_ns())
        post = Post(post_id = post_id, user_id = user_id, content = original_post.content, timestamp = int(time.time()), original_post_id = original_post.post_id)

        err = self.post_persistency.save_post(post)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to save repost")

        err = self.post_persistency.add_to_posts_list(post_id, user_id)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to add repost to user list")

        return RepostResponse(post=post)

    def DeletePost(self, request, context):
        post_id = request.post_id
        post, err = self.post_persistency.load_post(post_id)
        if err:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

        # if not self._check_permission(context, post["user_id"]):
        #     context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission denied")

        err = self.post_persistency.remove_post(post_id)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to delete post")

        err = self.post_persistency.remove_from_posts_list(post_id, post.user_id)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to remove post from user list")

        return DeletePostResponse()

    def GetUserPosts(self, request, context):
        user_id = request.user_id

        if not self.user_persistency.load_user(user_id):
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        posts, err = self.post_persistency.load_posts_list(user_id)
        
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to load user posts")

        print(posts)
        return GetUserPostsResponse(posts=posts)


def start_post_service(network, address, user_persistency, post_persistency):
    logging.info("Post service started")

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[
            UnaryLoggingInterceptor(),
            StreamLoggingInterceptor(),
            AuthInterceptor()
        ]
    )

    add_PostServiceServicer_to_server(PostService(user_persistency, post_persistency), server)
    server.add_insecure_port(address)
    server.start()
    server.wait_for_termination()
