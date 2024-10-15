from venv import logger
import grpc
from utils import USER
from comunication import get_authenticated_channel, get_host
from proto import users_pb2_grpc, users_pb2


def exists_user(user_id, token):
    host = get_host(USER)
    user_channel = get_authenticated_channel(host ,token)
    user_stub = users_pb2_grpc.UserServiceStub(user_channel)
    request = users_pb2.GetUserRequest(username=user_id)
    try:
        response = user_stub.GetUser(request)
        if response: return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred getting user: {error.code()}: {error.details()}")
        return None

