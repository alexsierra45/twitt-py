# from venv import logger
# import grpc
# from grpclib import GRPCError
# from proto import auth_pb2, auth_pb2_grpc, models_pb2, models_pb2_grpc

# channel = grpc.insecure_channel('localhost:5000')
# user_stub = auth_pb2_grpc.AuthStub(channel)

# def sign_up(email, username, name, password):
#     user = models_pb2.User(email=email, username=username, name=name, password=password)
#     request = auth_pb2.SignUpRequest(user=user)
#     try:
#         response = user_stub.SignUp(request)
#         print (response)
#         return True
#     except grpc.RpcError as error:
#         logger.error(f"An error occurred creating the user: {error.code()}: {error.details()}")
#         return False


# def login(username, password):
#     request = auth_pb2.LoginRequest(username=username, password=password)
#     print(request)

#     print("hola")
#     response = user_stub.Login(request)
#     print (response)
#     return True

from venv import logger
import grpc
from proto import auth_pb2, auth_pb2_grpc, models_pb2, models_pb2_grpc, posts_service_pb2, posts_service_pb2_grpc, follow_pb2, follow_pb2_grpc

# Canales para cada servicio
auth_channel = grpc.insecure_channel('localhost:5000')
user_channel = grpc.insecure_channel('localhost:5001')
post_channel = grpc.insecure_channel('localhost:5002')
follow_channel = grpc.insecure_channel('localhost:5003')

# Stubs para cada servicio
auth_stub = auth_pb2_grpc.AuthStub(auth_channel)
user_stub = models_pb2_grpc.UserStub(user_channel)
post_stub = posts_service_pb2_grpc.PostServiceStub(post_channel)
follow_stub = follow_pb2_grpc.FollowServiceStub(follow_channel)

def sign_up(email, username, name, password):
    user = models_pb2.User(email=email, username=username, name=name, password=password)
    request = auth_pb2.SignUpRequest(user=user)
    try:
        response = auth_stub.SignUp(request)
        print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred creating the user: {error.code()}: {error.details()}")
        return False

def login(username, password):
    request = auth_pb2.LoginRequest(username=username, password=password)
    try:
        response = auth_stub.Login(request)
        print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred logging in: {error.code()}: {error.details()}")
        return False

def create_post(user_id, content):
    request = posts_service_pb2.CreatePostRequest(user_id=user_id, content=content)
    try:
        response = post_stub.CreatePost(request)
        print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred creating the post: {error.code()}: {error.details()}")
        return False

def get_post(post_id):
    request = posts_service_pb2.GetPostRequest(post_id=post_id)
    try:
        response = post_stub.GetPost(request)
        print(response)
        return response.post
    except grpc.RpcError as error:
        logger.error(f"An error occurred fetching the post: {error.code()}: {error.details()}")
        return None

def delete_post(post_id):
    request = posts_service_pb2.DeletePostRequest(post_id=post_id)
    try:
        response = post_stub.DeletePost(request)
        print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred deleting the post: {error.code()}: {error.details()}")
        return False

def follow_user(user_id, target_user_id):
    request = follow_pb2.FollowUserRequest(user_id=user_id, target_user_id=target_user_id)
    try:
        response = follow_stub.FollowUser(request)
        print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred following the user: {error.code()}: {error.details()}")
        return False

def unfollow_user(user_id, target_user_id):
    request = follow_pb2.UnfollowUserRequest(user_id=user_id, target_user_id=target_user_id)
    try:
        response = follow_stub.UnfollowUser(request)
        print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred unfollowing the user: {error.code()}: {error.details()}")
        return False

def get_following(user_id):
    request = follow_pb2.GetFollowingRequest(user_id=user_id)
    try:
        response = follow_stub.GetFollowing(request)
        print(response)
        return response.following_usernames
    except grpc.RpcError as error:
        logger.error(f"An error occurred fetching the following list: {error.code()}: {error.details()}")
        return None



