from venv import logger
import grpc
from grpclib import GRPCError
from proto import auth_pb2, auth_pb2_grpc, models_pb2, models_pb2_grpc

channel = grpc.insecure_channel('localhost:5000')
user_stub = auth_pb2_grpc.AuthStub(channel)

def sign_up(email, username, name, password):
    user = models_pb2.User(email=email, username=username, name=name, password=password)
    request = auth_pb2.SignUpRequest(user=user)
    try:
        response = user_stub.SignUp(request)
        print (response)
        return True
    except grpc.InactiveRpcError as error:
        print("holaaaaaaaa")
        # print(error)
        logger.error(f"An error occurred creating the user: {error.status}: {error.details}")


def login(username, password):
    request = auth_pb2.LoginRequest(username=username, password=password)
    print(request)

    print("hola")
    response = user_stub.Login(request)
    print (response)
    return True




