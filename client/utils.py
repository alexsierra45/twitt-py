import grpc


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