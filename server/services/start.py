import socket
import sys
from chord.node import ChordNode
from persistency.user import UserPersitency
from chord.node_reference import ChordNodeReference
from services.auth_service import start_auth_service
from config import NETWORK

def start():
    ip = socket.gethostbyname(socket.gethostname())
    node = ChordNode(ip)

    if len(sys.argv) >= 2:
        other_ip = sys.argv[1]
        node.join(ChordNodeReference(other_ip, node.port))

    user_persitency = UserPersitency(node)

    start_auth_service(NETWORK, "0.0.0.0:5000", user_persitency)