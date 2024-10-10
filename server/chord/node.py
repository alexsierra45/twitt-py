import logging
import socket
import threading
import time

from chord.constants import *
from chord.node_reference import ChordNodeReference
from chord.storage import RAMStorage
from chord.utils import getShaRepr, inbetween
from chord.finger_table import FingerTable
from chord.discoverer import Discoverer
from chord.timer import Timer
from chord.elector import Elector


# Class representing a Chord node
class ChordNode:
    def __init__(self, ip: str, port: int = 8001, m: int = 160):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port
        self.ref = ChordNodeReference(self.ip, self.port)

        self.succ = self.ref  # Initial successor is itself
        self.succ_lock = threading.RLock() 

        self.pred = None  # Initially no predecessor
        self.pred_lock = threading.RLock()

        self.shutdown_event = threading.Event()

        self.finger = FingerTable(self, m) # Finger table
        self.storage = RAMStorage() # Dictionary to store key-value pairs
        self.timer = Timer(self) # Node clock
        self.elector = Elector(self, self.timer) # Leader regulator

        self.discoverer = Discoverer(self, self.succ_lock, self.pred_lock) # Broadcast discoverer

        # Start background threads for stabilization, fixing fingers, and checking predecessor
        threading.Thread(target=self.start_server, daemon=True).start()  # Start server thread
        threading.Thread(target=self.stabilize, daemon=True).start()  # Start stabilize thread
        threading.Thread(target=self.check_predecessor, daemon=True).start()  # Start check predecessor thread

    # Stabilize method to periodically verify and update the successor and predecessor
    def stabilize(self):
        while not self.shutdown_event.is_set():
            try:
                with self.succ_lock:
                    if self.succ.id != self.id or (self.succ.id == self.id and self.succ.pred.id != self.id):
                        logging.info('Stabilizing node')
                        
                        ok = self.succ.ping()
                        if ok:
                            pred = self.succ.pred
                            if pred.id != self.id:
                                if pred and inbetween(pred.id, self.id, self.succ.id):
                                    self.succ = pred
                                self.succ.notify(self.ref)
                            logging.info('Node stabilized')
                        else:
                            self.succ = self.ref
            except Exception as e:
                logging.error(f"Error in stabilize: {e}")

            logging.info(f"successor : {self.succ} predecessor {self.pred}")
            time.sleep(10)

    # Notify method to inform the node about another node
    def notify(self, node: 'ChordNodeReference'):
        if node.id == self.id:
            return
        if not self.pred or inbetween(node.id, self.pred.id, self.id):
            logging.info(f'Notify from {node.id}')
            # if not self.pred and self.id == self.succ.id:
            #     self.succ = node
            #     self.succ.notify(self.ref)
            self.pred = node
        else:
            logging.info(f'No update needed for node {node.id}')

    # Check predecessor method to periodically verify if the predecessor is alive
    def check_predecessor(self):
        while True:
            try:
                pred = self.pred
                if pred:
                    logging.info(f'Check predecessor {pred.id}')
                    ok = pred.ping()
                    if not ok:
                        logging.info(f'Predecessor {pred.id} has failed')
                        self.pred = None
            except Exception as e:
                self.pred = None
            time.sleep(10)

    def set_key(self, key: str, value: str) -> bool:
        key_hash = getShaRepr(key)
        node = self.finger.find_succ(key_hash)
        return node.store_key(key, value)

    # Store key method to store a key-value pair and replicate to the successor
    def store_key(self, key: str, value: str) -> bool:
        # key_hash = getShaRepr(key)
        # node = self.finger.find_succ(key_hash)
        # node.store_key(key, value)
        # self.storage[key] = value  # Store in the current node
        # self.succ.store_key(key, value)  # Replicate to the successor    
        return TRUE if self.storage.set(key, value) else FALSE
    
    def get_key(self, key: str) -> str:
        key_hash = getShaRepr(key)
        node = self.finger.find_succ(key_hash)
        return node.retrieve_key(key)

    # Retrieve key method to get a value for a given key
    def retrieve_key(self, key: str) -> str:
        # key_hash = getShaRepr(key)
        # node = self.finger.find_succ(key_hash)
        # return node.retrieve_key(key)
        return self.storage.get(key)

    # Start server method to handle incoming requests
    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            s.listen(10)

            while True:
                conn, addr = s.accept()

                data = conn.recv(1024).decode().split(',')

                data_resp = None
                option = int(data[0])

                logging.info(f'New connection from {addr}, operation {option}')

                server_response = ''

                if option == FIND_SUCCESSOR:
                    id = int(data[1])
                    data_resp = self.finger.find_succ(id)
                elif option == FIND_PREDECESSOR:
                    id = int(data[1])
                    data_resp = self.finger.find_pred(id)
                elif option == GET_SUCCESSOR:
                    data_resp = self.succ if self.succ else self.ref
                elif option == GET_PREDECESSOR:
                    data_resp = self.pred if self.pred else self.ref
                elif option == NOTIFY:
                    ip, port = data[1], int(data[2])
                    self.notify(ChordNodeReference(ip, port))
                elif option == CHECK_PREDECESSOR:
                    pass
                elif option == CLOSEST_PRECEDING_FINGER:
                    id = int(data[1])
                    data_resp = self.finger.closest_preceding_finger(id)
                elif option == STORE_KEY:
                    key, value = data[1], data[2]
                    server_response = self.store_key(key, value)
                elif option == RETRIEVE_KEY:
                    key = data[1]
                    server_response = self.retrieve_key(key)
                elif option == PING:
                    server_response = ALIVE
                elif option == STOP_DISCOVERING:
                    self.discoverer.stop_discovering()
                elif option == JOIN:
                    id = int(data[1])
                    ip = data[2]
                    server_response = self.discoverer.join(ChordNodeReference(ip, self.port))
                elif option == PING_LEADER:
                    id, time = int(data[1]), int(data[2])
                    server_response = self.elector.ping_leader(id, time)
                elif option == ELECTION:
                    id, ip, port = int(data[1]), data[2], int(data[3])
                    server_response = self.elector.election(id, ip, port)

                response = None
                if data_resp:
                    response = f'{data_resp.id},{data_resp.ip}'.encode()
                else:
                    response = f'{server_response}'.encode()

                conn.sendall(response)
                conn.close()