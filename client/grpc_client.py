import grpc
from proto import service_pb2, service_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
user_stub = service_pb2_grpc.UserServiceStub(channel)
post_stub = service_pb2_grpc.PostServiceStub(channel)

def sign_up(email, username, name, password):
    return user_stub.SignUp(service_pb2.SignUpRequest(email=email, username=username, name=name, password=password))

def login(username, password):
    return user_stub.Login(service_pb2.LoginRequest(username=username, password=password))

def follow_user(username, follow_username):
    return user_stub.FollowUser(service_pb2.FollowUserRequest(username=username, follow_username=follow_username))

def create_post(username, content):
    return post_stub.CreatePost(service_pb2.CreatePostRequest(username=username, content=content))

def get_posts(username):
    return post_stub.GetPosts(service_pb2.GetPostsRequest(username=username))
