import threading
from chord.node import ChordNode
from persistency.user import UserPersitency
from persistency.follow import FollowsPersitency
from persistency.post import PostPersitency
from services.follow_service import start_follow_service
from services.post_service import start_post_service
from services.users_service import start_user_service
from services.auth_service import start_auth_service
from config import NETWORK

def start():

    node = ChordNode()

    user_persistency = UserPersitency(node)
    post_persistency = PostPersitency(node)
    follow_persistency = FollowsPersitency(node)

# threading.Thread(target=self.stabilize, daemon=True).start()
    # start_auth_service(NETWORK, "localhost:50000", user_persitency)
    # start_user_service(NETWORK, "localhost:50001", user_persitency)
    # start_post_service(NETWORK, "localhost:50002", user_persitency, post_persistency)
    # start_follow_service(NETWORK, "localhost:50003", user_persitency, follow_persistency)


    threading.Thread(target=start_auth_service, args=(NETWORK, "localhost:50000", user_persistency)).start()
    threading.Thread(target=start_user_service, args=(NETWORK, "localhost:50001", user_persistency)).start()
    threading.Thread(target=start_post_service, args=(NETWORK, "localhost:50002", user_persistency, post_persistency)).start()
    threading.Thread(target=start_follow_service, args=(NETWORK, "localhost:50003", user_persistency, follow_persistency)).start()