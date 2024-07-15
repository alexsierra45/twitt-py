import logging
import grpc
from concurrent import futures
import time
import jwt
import re
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from config import PASSWORD, RSA_PRIVATE_KEY_PATH, RSA_PUBLIC_KEY_PATH
from persistency.user import UserPersitency
from services.interceptors import AuthInterceptor, StreamLoggingInterceptor, UnaryLoggingInterceptor
from interfaces.grpc.proto.auth_pb2 import LoginResponse, SignUpResponse
from interfaces.grpc.proto.auth_pb2_grpc import AuthServicer, add_AuthServicer_to_server

class AuthService(AuthServicer):
    def __init__(self, jwt_private_key, user_persistency: UserPersitency):
        self.jwt_private_key = jwt_private_key
        self.user_persistency = user_persistency

    def Login(self, request, context):
        username = request.username
        password = request.password
        user, err = self.user_persistency.load_user(username)

        if err:
            if err == grpc.StatusCode.NOT_FOUND:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Wrong username or password")
            else:
                context.abort(err, "Something went wrong")
            
        print(user)
        if not user or not verify_password(user.user_password, password):
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Wrong username or password")

        token = self.generate_token(user)
        return LoginResponse(token=token)

    def SignUp(self, request, context):
        user = request.user
        print(user)

        if not is_email_valid(user.email):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid email")

        exists, err = self.user_persistency.exists_user(user.username)
        if exists or err:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Fail to sign up")

        self.user_persistency.save_user(user)
        return SignUpResponse()

    def generate_token(self, user):
        payload = {
            "exp": time.time() + 72 * 3600,
            "iss": "auth.service",
            "iat": time.time(),
            "email": user.email,
            "sub": user.username,
            "name": user.name
        }
        return jwt.encode(payload, self.jwt_private_key, algorithm="RS256")

def verify_password(user_password, password):
    return user_password == password

def is_email_valid(email):
    email_regex = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    return email_regex.match(email) is not None

def start_auth_service(network, address, user_persistency):
    logging.info("Auth service started")

    private_key = load_private_key()

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[
            UnaryLoggingInterceptor(),
            StreamLoggingInterceptor(),
            AuthInterceptor()
        ]
    )

    add_AuthServicer_to_server(AuthService(private_key, user_persistency), server)
    server.add_insecure_port(address)
    # server.add_insecure_port(f"{network}:{address}")
    server.start()
    server.wait_for_termination()

def load_private_key():
    with open(RSA_PRIVATE_KEY_PATH, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=PASSWORD.encode(),
            backend=default_backend()
        )
    return private_key