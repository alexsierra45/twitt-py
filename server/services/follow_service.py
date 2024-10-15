import logging
import grpc
from concurrent import futures

from services.auth_service import check_permission
from services.interceptors import AuthInterceptor, StreamLoggingInterceptor, UnaryLoggingInterceptor
from interfaces.grpc.proto.follow_pb2 import FollowUserResponse, UnfollowUserResponse, GetFollowingResponse
from interfaces.grpc.proto.follow_pb2_grpc import FollowServiceServicer, add_FollowServiceServicer_to_server

class FollowService(FollowServiceServicer):
    def __init__(self, user_persistency, follow_persistency):
        self.user_persistency = user_persistency
        self.follow_persistency = follow_persistency

    def FollowUser(self, request, context):
        username = request.user_id
        target_username = request.target_user_id

        if not check_permission(self.user_persistency, username):
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission denied")

        if username == target_username:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Cannot follow yourself")

        if not self.user_persistency.exists_user(username):
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        if not self.user_persistency.exists_user(target_username):
            context.abort(grpc.StatusCode.NOT_FOUND, "Target user not found")

        ok, err = self.follow_persistency.add_to_following_list(username, target_username)

        if err:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to follow user: {err}")

        if not ok:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Already following user {target_username}")

        return FollowUserResponse()

    def UnfollowUser(self, request, context):
        username = request.user_id
        target_username = request.target_user_id

        if not check_permission(self.user_persistency, username):
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission denied")

        if username == target_username:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Cannot unfollow yourself")

        if not self.user_persistency.exists_user(username):
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        if not self.user_persistency.exists_user(target_username):
            context.abort(grpc.StatusCode.NOT_FOUND, "Target user not found")

        ok, err = self.follow_persistency.remove_from_following_list(username, target_username)

        if err:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to unfollow user: {err}")

        if not ok:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Not following user {target_username}")

        return UnfollowUserResponse()

    def GetFollowing(self, request, context):
        username = request.user_id

        if not self.user_persistency.exists_user(username):
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        following, err = self.follow_persistency.load_following_list(username)

        if err:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to load following list: {err}")

        return GetFollowingResponse(following_usernames=following)


def start_follow_service(network, address, user_persistency, follow_persistency):
    logging.info("Follow Service Started")

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[
            UnaryLoggingInterceptor(),
            StreamLoggingInterceptor(),
            AuthInterceptor()
        ]
    )

    add_FollowServiceServicer_to_server(FollowService(user_persistency, follow_persistency), server)
    server.add_insecure_port(address)
    server.start()
    server.wait_for_termination()
