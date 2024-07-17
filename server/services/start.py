from chord.node import ChordNode
from persistency.user import UserPersitency
from server.persistency.follow import FollowsPersitency
from server.persistency.post import PostPersitency
from server.services.follow_service import start_follow_service
from server.services.post_service import start_post_service
from server.services.users_service import start_user_service
from services.auth_service import start_auth_service
from config import NETWORK

def start():

    node = ChordNode()

    user_persitency = UserPersitency(node)
    post_persistency = PostPersitency(node)
    follow_persistency = FollowsPersitency(node)

    start_auth_service(NETWORK, "localhost:5000", user_persitency)
    start_user_service(NETWORK, "localhost:5001", user_persitency)
    start_post_service(NETWORK, "localhost:5002", user_persitency, post_persistency)
    start_follow_service(NETWORK, "localhost:5003", user_persitency, follow_persistency)