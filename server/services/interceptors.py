from grpc_interceptor import ServerInterceptor
import grpc
import logging
import time
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from config import RSA_PUBLIC_KEY_PATH

class AuthInterceptor(ServerInterceptor):
    def __init__(self):
        self.public_key = load_public_key()

    def intercept(self, method, request, context, method_name):
        method_name = method_name.split('/')[-1]

        if method_name in ["Login", "SignUp"]:
            return method(request, context)
        
        metadata = context.invocation_metadata()
        token = None
        for key, value in metadata:
            if key == 'authorization':
                token = value
                break

        if not token:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Valid token required.")
        
        try:
            jwt.decode(token, self.public_key, algorithms=["RS256"])
        except jwt.ExpiredSignatureError:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token has expired.")
        except jwt.InvalidTokenError:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid token.")

        return method(request, context)
    
def load_public_key():
    with open(RSA_PUBLIC_KEY_PATH, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key

class UnaryLoggingInterceptor(ServerInterceptor):
    def intercept(self, method, request, context, method_name):
        start_time = time.time()
        peer = context.peer()

        logging.info(f"Request received - Method:{method_name} From:{peer}")

        response, exception = None, None
        try:
            response = method(request, context)
        except Exception as ex:
            exception = ex

        duration = time.time() - start_time
        logging.info(f"Request completed - Method:{method_name}\tDuration:{duration}\tError:{exception}")

        if exception:
            raise exception

        return response

class StreamLoggingInterceptor(ServerInterceptor):
    def intercept(self, method, request_or_iterator, context, method_name):
        start_time = time.time()
        peer = context.peer()

        logging.info(f"Streaming request received - Method:{method_name} From:{peer}")

        response, exception = None, None
        try:
            response = method(request_or_iterator, context)
        except Exception as ex:
            exception = ex

        duration = time.time() - start_time
        logging.info(f"Streaming Request completed - Method:{method_name}\tDuration:{duration}\tError:{exception}")

        if exception:
            raise exception

        return response
