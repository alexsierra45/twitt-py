import logging
import grpc


BROADCAST_PORT = 11000
BROADCAST_REQUEST_PORT = 12000

ALIVE = 'Im alive'
ARE_YOU = 'Are you a chord?'
YES_IM = 'Yes, I am a chord'

AUTH = 50000
USER = 50001
POST = 50002
FOLLOW = 50003


logger = logging.getLogger(__name__)


class AuthInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.UnaryStreamClientInterceptor):
    def __init__(self, token):
        self.token = token

    def intercept_unary_unary(self, continuation, client_call_details, request):
        metadata = client_call_details.metadata if client_call_details.metadata is not None else []
        metadata = list(metadata) + [('authorization', self.token)]
        client_call_details = client_call_details._replace(metadata=metadata)
        return continuation(client_call_details, request)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        metadata = client_call_details.metadata if client_call_details.metadata is not None else []
        metadata = list(metadata) + [('authorization', self.token)]
        client_call_details = client_call_details._replace(metadata=metadata)
        return continuation(client_call_details, request)
    


    