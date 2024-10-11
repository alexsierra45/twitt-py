from venv import logger
import grpc
from utils import AUTH
from proto import auth_pb2, auth_pb2_grpc, models_pb2
from comunication import get_host


def sign_up(email, username, name, password):
    host = get_host(AUTH)
    auth_channel = grpc.insecure_channel(host)
    auth_stub = auth_pb2_grpc.AuthStub(auth_channel)
    user = models_pb2.User(email=email, username=username, name=name, password_hash=password)
    request = auth_pb2.SignUpRequest(user=user)
    try:
        response = auth_stub.SignUp(request)
        # print(response)
        return True
    except grpc.RpcError as error:
        logger.error(f"An error occurred creating the user: {error.code()}: {error.details()}")
        return False

def login(username, password):
    host = get_host(AUTH)
    auth_channel = grpc.insecure_channel(host)
    auth_stub = auth_pb2_grpc.AuthStub(auth_channel)
    request = auth_pb2.LoginRequest(username=username, password=password)
    try:
        response = auth_stub.Login(request)
        # print(response)
        return response.token
    except grpc.RpcError as error:
        logger.error(f"An error occurred logging in: {error.code()}: {error.details()}")
        return None