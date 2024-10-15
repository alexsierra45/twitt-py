from venv import logger
import grpc
from cache import Storage
from utils import POST
from comunication import get_authenticated_channel, get_host
from proto import models_pb2, posts_service_pb2, posts_service_pb2_grpc


def create_post(user_id, content, token):
    host = get_host(POST)
    post_channel = get_authenticated_channel(host ,token)
    post_stub = posts_service_pb2_grpc.PostServiceStub(post_channel)
    request = posts_service_pb2.CreatePostRequest(user_id=user_id, content=content)
    try:
        response = post_stub.CreatePost(request)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred creating the post: {error.code()}: {error.details()}")
        return False

def get_post(post_id, token):
    host = get_host(POST)
    post_channel = get_authenticated_channel(host ,token)
    post_stub = posts_service_pb2_grpc.PostServiceStub(post_channel)
    request = posts_service_pb2.GetPostRequest(post_id=post_id)
    try:
        response = post_stub.GetPost(request)
        return response.post
    except grpc.RpcError as error:
        logger.error(f"An error occurred fetching the post: {error.code()}: {error.details()}")
        return None

def delete_post(post_id, token):
    host = get_host(POST)
    post_channel = get_authenticated_channel(host ,token)
    post_stub = posts_service_pb2_grpc.PostServiceStub(post_channel)
    request = posts_service_pb2.DeletePostRequest(post_id=post_id)
    try:
        response = post_stub.DeletePost(request)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred deleting the post: {error.code()}: {error.details()}")
        return False
    
def repost(user_id, original_post_id, token):
    host = get_host(POST)
    post_channel = get_authenticated_channel(host ,token)
    post_stub = posts_service_pb2_grpc.PostServiceStub(post_channel)
    request = posts_service_pb2.RepostRequest(user_id=user_id, original_post_id=original_post_id)
    try:
        response = post_stub.Repost(request)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred reposting: {error.code()}: {error.details()}")
        return False

async def get_user_posts(user_id, token, request = False):
    if not request:
        cached_posts = await Storage.async_disk_get(f"{user_id}_posts", default=None)
        if cached_posts is not None:
            value = [models_pb2.Post.FromString(v) for v in cached_posts]
            return value
        
    host = get_host(POST)
    post_channel = get_authenticated_channel(host ,token)
    post_stub = posts_service_pb2_grpc.PostServiceStub(post_channel)
    request = posts_service_pb2.GetUserPostsRequest(user_id=user_id)

    try:
        response = post_stub.GetUserPosts(request)
        new_Posts = []
        for post in response.posts:
            new_post = models_pb2.Post( post_id = post.post_id, user_id = post.user_id, content = post.content, timestamp = post.timestamp, original_post_id = post.original_post_id)
            new_Posts.append(new_post)
        serialized_value = [v.SerializeToString() for v in new_Posts]   
        await Storage.async_disk_store(f"{user_id}_posts", serialized_value)
        return new_Posts
    except grpc.RpcError as error:
        logger.error(f"An error occurred fetching user posts: {error.code()}: {error.details()}")
        return None    