from chord.node import ChordNode
from persistency.user import UserPersitency
from services.auth_service import start_auth_service
from config import NETWORK

def start():

    node = ChordNode()

    user_persitency = UserPersitency(node)

    start_auth_service(NETWORK, "172.31.141.188:5000", user_persitency)