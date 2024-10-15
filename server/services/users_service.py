import logging
import grpc
from concurrent import futures
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from config import PASSWORD, RSA_PRIVATE_KEY_PATH, RSA_PUBLIC_KEY_PATH
from persistency.user import UserPersitency
from services.auth_service import is_email_valid
from services.interceptors import AuthInterceptor, StreamLoggingInterceptor, UnaryLoggingInterceptor
from interfaces.grpc.proto.users_pb2 import GetUserResponse, EditUserResponse
from interfaces.grpc.proto.users_pb2_grpc import UserServiceServicer, add_UserServiceServicer_to_server

class UserService(UserServiceServicer):
    def __init__(self, user_persistency: UserPersitency):
        self.user_persistency = user_persistency

    def GetUser(self, request, context):
        username = request.username

        user, err = self.user_persistency.load_user(username)

        if err:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        
        user.password_hash = ""

        return GetUserResponse(user=user)

    def EditUser(self, request, context):
        username = request.user.username

        # if not check_permission(context, username):
        #     context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission denied")

        user, err = self.user_persistency.load_user(username)

        if err:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        if not is_email_valid(request.user.email):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid email")

        user.name = request.user.name
        user.email = request.user.email

        if not self.user_persistency.save_user(user):
            context.abort(grpc.StatusCode.INTERNAL, "Failed to save user")

        return EditUserResponse()

def start_user_service(network, address, user_persistency):
    logging.info("User service started")

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[
            UnaryLoggingInterceptor(),
            StreamLoggingInterceptor(),
            AuthInterceptor()
        ]
    )

    add_UserServiceServicer_to_server(UserService(user_persistency), server)
    server.add_insecure_port(address)
    server.start()
    server.wait_for_termination()
