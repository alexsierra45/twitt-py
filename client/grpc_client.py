from typing import Optional
from venv import logger
import grpc
import jwt
from cache import Storage
from utils import AuthInterceptor
from proto import auth_pb2, auth_pb2_grpc, models_pb2, models_pb2_grpc, posts_service_pb2, posts_service_pb2_grpc, follow_pb2, follow_pb2_grpc, users_pb2_grpc, users_pb2


def get_authenticated_channel(channel, token):
    auth_interceptor = AuthInterceptor(token)
    return grpc.intercept_channel(grpc.insecure_channel(channel), auth_interceptor)

user_channel = grpc.insecure_channel('localhost:50001')

user_stub = users_pb2_grpc.UserServiceStub(user_channel)

def sign_up(email, username, name, password):
    auth_channel = grpc.insecure_channel('localhost:50000')
    auth_stub = auth_pb2_grpc.AuthStub(auth_channel)
    user = models_pb2.User(email=email, username=username, name=name, password_hash=password)
    request = auth_pb2.SignUpRequest(user=user)
    try:
        response = auth_stub.SignUp(request)
        print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred creating the user: {error.code()}: {error.details()}")
        return False

def login(username, password):
    auth_channel = grpc.insecure_channel('localhost:50000')
    auth_stub = auth_pb2_grpc.AuthStub(auth_channel)
    request = auth_pb2.LoginRequest(username=username, password=password)
    try:
        response = auth_stub.Login(request)
        # print(response)
        return response.token
    except grpc.RpcError as error:
        logger.error(f"An error occurred logging in: {error.code()}: {error.details()}")
        return None

def create_post(user_id, content, token):
    post_channel = get_authenticated_channel('localhost:50002',token)
    post_stub = posts_service_pb2_grpc.PostServiceStub(post_channel)
    request = posts_service_pb2.CreatePostRequest(user_id=user_id, content=content)
    try:
        response = post_stub.CreatePost(request)
        print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred creating the post: {error.code()}: {error.details()}")
        return False

def get_post(post_id, token):
    post_channel = get_authenticated_channel('localhost:50002',token)
    post_stub = posts_service_pb2_grpc.PostServiceStub(post_channel)
    request = posts_service_pb2.GetPostRequest(post_id=post_id)
    try:
        response = post_stub.GetPost(request)
        print(response)
        return response.post
    except grpc.RpcError as error:
        logger.error(f"An error occurred fetching the post: {error.code()}: {error.details()}")
        return None

def delete_post(post_id, token):
    post_channel = get_authenticated_channel('localhost:50002',token)
    post_stub = posts_service_pb2_grpc.PostServiceStub(post_channel)
    request = posts_service_pb2.DeletePostRequest(post_id=post_id)
    try:
        response = post_stub.DeletePost(request)
        print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred deleting the post: {error.code()}: {error.details()}")
        return False
    
def repost(user_id, original_post_id, token):
    post_channel = get_authenticated_channel('localhost:50002',token)
    post_stub = posts_service_pb2_grpc.PostServiceStub(post_channel)
    request = posts_service_pb2.RepostRequest(user_id=user_id, original_post_id=original_post_id)
    try:
        response = post_stub.Repost(request)
        print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred reposting: {error.code()}: {error.details()}")
        return False

async def get_user_posts(user_id, token, request = False):
    # if not request:
    #     cached_posts = await Storage.async_disk_get(f"{user_id}_posts", default=None)
    #     if cached_posts is not None:
    #         value = [models_pb2.Post.FromString(v) for v in cached_posts]
    #         return value
        
    post_channel = get_authenticated_channel('localhost:50002',token)
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
        print(new_Posts)
        return new_Posts
    except grpc.RpcError as error:
        logger.error(f"An error occurred fetching user posts: {error.code()}: {error.details()}")
        return None    

def follow_user(user_id, target_user_id, token):
    follow_channel = get_authenticated_channel('localhost:50003',token)
    follow_stub = follow_pb2_grpc.FollowServiceStub(follow_channel)
    request = follow_pb2.FollowUserRequest(user_id=user_id, target_user_id=target_user_id)
    try:
        response = follow_stub.FollowUser(request)
        print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred following the user: {error.code()}: {error.details()}")
        return False

def unfollow_user(user_id, target_user_id, token):
    follow_channel = get_authenticated_channel('localhost:50003',token)
    follow_stub = follow_pb2_grpc.FollowServiceStub(follow_channel)
    request = follow_pb2.UnfollowUserRequest(user_id=user_id, target_user_id=target_user_id)
    try:
        response = follow_stub.UnfollowUser(request)
        print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred unfollowing the user: {error.code()}: {error.details()}")
        return False

async def get_following(user_id, token, request = False):
    if not request:
        cached_following = await Storage.async_disk_get(f"{user_id}_following", default=None)
        if cached_following is not None:
            return cached_following
        
    follow_channel = get_authenticated_channel('localhost:50003',token)
    follow_stub = follow_pb2_grpc.FollowServiceStub(follow_channel)
    request = follow_pb2.GetFollowingRequest(user_id=user_id)
    try:
        response = follow_stub.GetFollowing(request)
        print(response)
        following_usernames = [username for username in response.following_usernames]
        await Storage.async_disk_store(f"{user_id}_posts", following_usernames)
        return response.following_usernames
    except grpc.RpcError as error:
        logger.error(f"An error occurred fetching the following list: {error.code()}: {error.details()}")
        return None

def exists_user(user_id, token):
    user_channel = get_authenticated_channel('localhost:50001',token)
    user_stub = users_pb2_grpc.UserServiceStub(user_channel)
    request = users_pb2.GetUserRequest(username=user_id)
    try:
        response = user_stub.GetUser(request)
        if response: return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred fetching the following list: {error.code()}: {error.details()}")
        return None


