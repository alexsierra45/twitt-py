import logging
import socket
import struct
import threading
import time
import uuid

from chord.node_reference import ChordNodeReference
from chord.constants import FALSE, TRUE

MCAST_GRP = '224.0.0.1'
MCAST_PORT = 5007

class Discoverer:
    def __init__(self, node, succ_lock, pred_lock) -> None:
        self.node = node
        self.succ_lock = succ_lock
        self.pred_lock = pred_lock
        self.times = 2
        self.joined = False
        self.node_id = str(uuid.uuid4())  # Unique identifier for this node

        threading.Thread(target=self.send_announcement, daemon=True).start()  # Start multicast discover sender
        threading.Thread(target=self.listen_for_announcements, daemon=True).start()  # Start multicast discover listener

    def send_announcement(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            
            logging.info(f'Looking for a chord ring !!!')
            while self.times > 0:
                message = f"NODE:{self.node.ip}:{self.node_id}"
                print(message)
                s.sendto(message.encode(), (MCAST_GRP, MCAST_PORT))
                time.sleep(5)
                self.times = self.times - 1
            if self.joined:
                logging.info('Chord ring discovered :)')
            else:
                logging.info('No chord ring was discovered :(')

    # def mcast_call(message, mcast_addr, port):
    #     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    #     s.sendto(message.encode(), (mcast_addr, port))
    #     s.close()

    def stop_discovering(self):
        self.times = 0
        self.joined = True

        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # membership = socket.inet_aton(self.mcast_adrr) + socket.inet_aton('0.0.0.0')
        # s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # s.bind(('', int(PORT)))
    
    def listen_for_announcements(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            membership = socket.inet_aton(MCAST_GRP) + socket.inet_aton('0.0.0.0')
            s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            s.bind(('', int(MCAST_PORT)))


            # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # s.bind(('', MCAST_PORT))

            # mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
            # s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            while True:
                message, addr = s.recvfrom(1024)
                if not message:
                    continue  # Ignore empty messages
                if message.decode().startswith("NODE:"):
                    ip, unique_id = message.decode().split(":")[1:]
                    if unique_id == self.node_id:
                        continue  # Ignore messages from itself
                    logging.info(f"Discovered node: {ip}")
                    node = ChordNodeReference(ip, self.node.port)
                    if node.join(self.node.ref):
                        node.stop_discovering()

    def join(self, node: 'ChordNodeReference'):
        try:
            with self.succ_lock and self.pred_lock:
                print('wadafaaaa')
                print(self.node.ip)
                self.node.pred = None
                self.node.succ = node.find_successor(self.node.id)
                print(self.node.succ.ip)
                self.node.succ.notify(self.node.ref)
                logging.info(f'Joining node {node.ip}')
                return TRUE
        except Exception as e:
            logging.error(f'Error joining to chord ring: {e}')
            return FALSE