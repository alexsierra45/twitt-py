import grpc
from proto import auth_pb2, auth_pb2_grpc

channel = grpc.insecure_channel('172.31.141.188:5000')
user_stub = auth_pb2_grpc.AuthServiceStub(channel)

def sign_up(email, username, name, password):
    return user_stub.SignUp(auth_pb2.SignUpRequest(email=email, username=username, name=name, password=password))

def login(username, password):
    return user_stub.Login(auth_pb2.LoginRequest(username=username, password=password))
