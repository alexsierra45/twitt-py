import logging
import socket
from venv import logger
import grpc
from cache import Storage
from utils import ARE_YOU, BROADCAST_PORT, BROADCAST_REQUEST_PORT, YES_IM, AuthInterceptor


def update_server():
    server = discover()
    if server:
        print("encontre algo")
        Storage.store('server', server)
    else:
        logger.info("No servers found")
        Storage.delete('server')


def discover():
        logging.info('Looking for a chord ring via broadcast!!!')
        timeout = 2

        broadcast_addr = ('<broadcast>', BROADCAST_PORT)

        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            conn.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            conn.bind(('', int(BROADCAST_REQUEST_PORT)))
        except Exception as e:
            logging.info("UNKNOWN error")

        message = f"{ARE_YOU};1".encode()
        conn.sendto(message, broadcast_addr)

        buffer = bytearray(1024)

        conn.settimeout(2)

        for _ in range(timeout):
            try:
                nn, addr = conn.recvfrom_into(buffer)
                res = buffer[:nn].decode().split(";")
                message = res[0]

                if message == YES_IM and len(res) == 2:
                    return addr[0]
                
            except socket.timeout:
                continue
            except Exception as e:
                logging.error("Error receiving message:", e)

        logging.info("No chord ring was discovered :(")


def is_server_alive(host, port, timeout=1):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False

def get_host(service):
    server = Storage.get('server', default='localhost')

    if not is_server_alive(server, int(service)):
        update_server()
        server = Storage.get('server', default='localhost')

    if server and is_server_alive(server, int(service)):
        return (f"{server}:{service}")

    raise ConnectionError("No available servers are alive.")

def get_authenticated_channel(host, token):
    auth_interceptor = AuthInterceptor(token)
    return grpc.intercept_channel(grpc.insecure_channel(host), auth_interceptor)
