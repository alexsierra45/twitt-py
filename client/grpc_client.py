import grpc
from proto import auth_pb2, auth_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
user_stub = auth_pb2_grpc.UserServiceStub(channel)

def sign_up(email, username, name, password):
    return user_stub.SignUp(auth_pb2.SignUpRequest(email=email, username=username, name=name, password=password))

def login(username, password):
    return user_stub.Login(auth_pb2.LoginRequest(username=username, password=password))
