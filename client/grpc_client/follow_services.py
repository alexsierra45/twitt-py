from venv import logger
import grpc
from cache import Storage
from utils import FOLLOW
from comunication import get_authenticated_channel, get_host
from proto import follow_pb2, follow_pb2_grpc


def follow_user(user_id, target_user_id, token):
    host = get_host(FOLLOW)
    follow_channel = get_authenticated_channel(host ,token)
    follow_stub = follow_pb2_grpc.FollowServiceStub(follow_channel)
    request = follow_pb2.FollowUserRequest(user_id=user_id, target_user_id=target_user_id)
    try:
        response = follow_stub.FollowUser(request)
        # print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred following the user: {error.code()}: {error.details()}")
        return False

def unfollow_user(user_id, target_user_id, token):
    host = get_host(FOLLOW)
    follow_channel = get_authenticated_channel(host ,token)
    follow_stub = follow_pb2_grpc.FollowServiceStub(follow_channel)
    request = follow_pb2.UnfollowUserRequest(user_id=user_id, target_user_id=target_user_id)
    try:
        response = follow_stub.UnfollowUser(request)
        # print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred unfollowing the user: {error.code()}: {error.details()}")
        return False

async def get_following(user_id, token, request = False):
    if not request:
        cached_following = await Storage.async_disk_get(f"{user_id}_following", default=None)
        if cached_following is not None:
            return cached_following
        
    host = get_host(FOLLOW)
    follow_channel = get_authenticated_channel(host ,token)
    follow_stub = follow_pb2_grpc.FollowServiceStub(follow_channel)
    request = follow_pb2.GetFollowingRequest(user_id=user_id)
    try:
        response = follow_stub.GetFollowing(request)
        # print(response)
        following_usernames = [username for username in response.following_usernames]
        await Storage.async_disk_store(f"{user_id}_following", following_usernames)
        return response.following_usernames
    except grpc.RpcError as error:
        logger.error(f"An error occurred fetching the following list: {error.code()}: {error.details()}")
        return None