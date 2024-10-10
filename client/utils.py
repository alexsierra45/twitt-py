import logging
import random
import socket
import time
from venv import logger
import grpc

from cache import Storage


BROADCAST_PORT = 11000

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
    
def get_host(service):
    server = random.choice(Storage.get('server', default=['localhost']))
    return f"{server}:{service}"    

def check_host(server):
    timeout = 5

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout()

    try:
        sock.sendto(b"Are you a chord?;client", (server, BROADCAST_PORT))
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response, address = sock.recvfrom(1024)
                logger.info(f"Received {response} from {address}")
                if response.startswith(b"Yes, I am a chord"):
                    return True
            except socket.timeout:
                continue
        return False    
    except Exception as e:
        logger.error(f"Error during discovery: {e}")
    finally:
        sock.close()

def discover(timeout: int = 5):
    broadcast = '255.255.255.255'
    logger.info(f"Discovering on {broadcast}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)

    try:
        sock.sendto(b"Are you a chord?;client", (broadcast, BROADCAST_PORT))
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response, address = sock.recvfrom(1024)
                logger.info(f"Received {response} from {address}")
                if response.startswith(b"Yes, I am a chord"):
                    yield address[0]
            except socket.timeout:
                # Timeout for this iteration, continue listening
                continue
    except Exception as e:
        logger.error(f"Error during discovery: {e}")
    finally:
        sock.close()



def update_servers():
    servers = list(discover())
    if servers:
        logger.info(f"Found {len(servers)} servers: {servers}")
        Storage.store('server', servers)
    else:
        logger.info("No servers found")
        Storage.delete('server')