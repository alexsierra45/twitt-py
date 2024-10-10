import logging
import socket
import threading
import time

from chord.constants import *
from chord.node_reference import ChordNodeReference
from chord.storage import Data, RAMStorage
from chord.utils import getShaRepr, inbetween
from chord.finger_table import FingerTable
from chord.discoverer import Discoverer
from chord.timer import Timer
from chord.elector import Elector
from chord.dynamic_list import DynamicList
from chord.replicator import Replicator

# Class representing a Chord node
class ChordNode:
    def __init__(self, ip: str, port: int = 8001, m: int = 160, c: int = 3):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port
        self.ref = ChordNodeReference(self.ip, self.port)
        self.c = c
 
        self.successors = DynamicList[ChordNodeReference](c)
        self.succ_lock = threading.RLock() 

        self.predecessors = DynamicList[ChordNodeReference](c)
        self.pred_lock = threading.RLock()

        self.shutdown_event = threading.Event()

        threading.Thread(target=self.start_server, daemon=True).start()  # Start server thread

        self.finger = FingerTable(self, m) # Finger table
        self.timer = Timer(self) # Node clock
        self.elector = Elector(self, self.timer) # Leader regulator
        self.discoverer = Discoverer(self, self.succ_lock, self.pred_lock, self.elector, self.finger) # Chord ring discoverer
        self.replicator = Replicator(self) # Data replicator

        self.discoverer.create_ring_or_join()

        threading.Thread(target=self.stabilize, daemon=True).start() # Start stabilize thread
        threading.Thread(target=self.check_predecessor, daemon=True).start() # Start check predecessor thread
        threading.Thread(target=self.check_successor, daemon=True).start() # Start check predecessor thread
        threading.Thread(target=self.fix_successors, daemon=True).start() # Start fixing successors
        threading.Thread(target=self.finger.fix_fingers, daemon=True).start() # Start fix fingers thread
        threading.Thread(target=self.discoverer.discover_and_join, daemon=True).start() # Start discovering new rings
        threading.Thread(target=self.elector.check_leader, daemon=True).start() # Start check leader thread
        threading.Thread(target=self.discoverer.listen_for_announcements, daemon=True).start() # Start fix fingers thread
        threading.Thread(target=self.elector.election_thread, daemon=True).start() # Start election thread
        threading.Thread(target=self.timer.update_time, daemon=True).start() # Start update time thread


    # Stabilize method to periodically verify and update the successor and predecessor
    def stabilize(self):
        while not self.shutdown_event.is_set():
            try:
                logging.info('Stabilizing node')
                with self.succ_lock:
                    succ = self.successors.get_index(0)
                succ_pred = succ.pred
                if (succ.id == self.id and succ_pred.id != self.id) or inbetween(succ_pred.id, self.id, succ.id):
                    logging.info(f'Notifing {succ_pred}')
                    with self.succ_lock:
                        self.successors.set_index(0, succ_pred)
                    succ_pred.notify(self.ref)
                    # n.replicateAllData(pred)
                else:
                    if succ.id != self.id:
                        succ.notify(self.ref)
                logging.info('Node stabilized')
            except Exception as e:
                logging.error(f"Error in stabilize: {e}")

            with self.succ_lock and self.pred_lock:
                succ = self.successors.get_index(0)
                pred = self.predecessors.get_index(0)
            logging.info(f"successor : {succ} predecessor {pred}")
            time.sleep(10)

    # Notify method to inform the node about another node
    def notify(self, node: 'ChordNodeReference'):
        with self.pred_lock:
            pred = self.predecessors.get_index(0)
            if pred.id == self.id or inbetween(node.id, pred.id, self.id):
                logging.info(f'Notify from {node.id}')
                if pred.id == self.id:
                    self.predecessors.remove_index(0)
                self.predecessors.set_index(0, node)

                # new predecessor storage
                # n.newPredecessorStorage()
            else:
                logging.info(f'No update needed for node {node.id}')

    # Check successor method to periodically verify if the successor is alive
    def check_successor(self):
        while True:
            with self.succ_lock:
                succ = self.successors.get_index(0)
            if succ.id != self.id:
                logging.info(f'Check successor {succ.id}')
                ok = succ.ping()
                if not ok:
                    logging.info(f'Successor {succ.id} has failed')
                    with self.succ_lock:
                        succs_len = len(self.successors)
                        if succs_len == 1:
                            self.successors.remove_index(0)
                            self.successors.set_index(0, self.ref)
                        else:
                            self.successors.remove_index(0)
            time.sleep(10)

    # Check predecessor method to periodically verify if the predecessor is alive
    def check_predecessor(self):
        while True:
            with self.pred_lock:
                pred = self.predecessors.get_index(0)
            if pred and pred.id != self.id:
                logging.info(f'Check predecessor {pred.id}')
                ok = pred.ping()
                if not ok:
                    logging.info(f'Predecessor {pred.id} has failed')
                    with self.pred_lock:
                        preds_len = len(self.predecessors)
                        if preds_len == 1:
                            self.predecessors.remove_index(0)
                            self.predecessors.set_index(0, self.ref)
                        else:
                            self.predecessors.remove_index(0)

                    # n.failPredecessorStorage(predecessor.id)
            time.sleep(10)

    def get_successor_and_notify(self, index, ip):
        node = ChordNodeReference(ip, self.port)

        with self.succ_lock:
            succ = self.successors.get_index(0)

        with self.pred_lock:
            if len(self.predecessors) <= index or self.predecessors.get_index(index).id != node.id:
                if len(self.predecessors) < index:
                    index = len(self.predecessors)
                self.predecessors.set_index(index, node)
        return succ
    
    def fix_successors(self):
        logging.info('Fix successors thread started')

        next = 0
        while not self.shutdown_event.is_set():
            succ = self.successors.get_index(0)
            if succ.id == self.id:
                continue
            next = self.fix_successor(next)
            time.sleep(15)

    def fix_successor(self, index: int) -> int:
        logging.info(f'Fixing successor {index}')
        succ: ChordNodeReference = None

        with self.succ_lock:
            succs_len = len(self.successors)
            if succs_len == 0:
                return 0

            if index < succs_len:
                succ = self.successors.get_index(index)
            last = self.successors.get_index(succs_len - 1)

        if succ is None:
            return 0
        
        if succ.id == self.id and succs_len == 1:
            return 0
        
        if succs_len != 1 and last.id == self.id:
            with self.succ_lock:
                succs_len -= 1
                self.successors.remove_index(succs_len)

        with self.succ_lock:
            try:
                succ = succ.get_successor_and_notify(index, self.ip)
                if succ.id == self.id or index == self.c - 1:
                    return 0
                
                if index == succs_len - 1:
                    self.successors.set_index(index + 1, succ)
                    # replicate all data
                    # self.replicate_all_dat(succ)
                    return (index + 1) % len(self.successors)
                
                next_succ = self.successors.get_index(index + 1)
                if next_succ.id != succ.id:
                    self.successors.set_index(index + 1, succ)

                    find = False
                    for _ in range(len(self.successors)):
                        if succ.id == self.successors.get_index(index).id:
                            find = True

                    if find:
                        # replicate all data
                        # self.replicate_all_dat(succ)
                        pass

                return (index + 1) % len(self.successors)
            except Exception as e:
                logging.error(f'Error fixing succesor {index}: {e}')
                with self.succ_lock:
                    self.successors.remove_index(index)
                    if len(self.successors) == 0:
                        self.successors.set_index(0, self.ref)
                    return index % len(self.successors)
                
    def get_key(self, key: str) -> str:
        logging.info(f'Get key {key}')

        key_hash = getShaRepr(key)
        with self.succ_lock:
            succ = self.finger.find_succ(key_hash)
        data = succ.retrieve_key(key)

        return data.value

    def set_key(self, key: str, value: str) -> bool:
        logging.info(f'Set key {key} with value {value}')

        key_hash = getShaRepr(key)
        with self.succ_lock:
            succ = self.finger.find_succ(key_hash)

        with self.timer.time_lock:
            time = self.timer.time_counter

        response = succ.store_key(key, value, time, True)
        
        return response
    
    def remove_key(self, key: str) -> bool:
        logging.info(f'Remove key {key}')

        key_hash = getShaRepr(key)
        with self.succ_lock:
            succ = self.finger.find_succ(key_hash)

        with self.timer.time_lock:
            time = self.timer.time_counter

        response = succ.delete_key()

        return response

    # Start server method to handle incoming requests
    def start_server(self):
        logging.info('Starting main thread')

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
                    pred = self.finger.find_pred(id)
                    data_resp = pred if pred else self.ref
                elif option == GET_SUCCESSOR:
                    succ = self.successors.get_index(0)
                    data_resp = succ if succ else self.ref
                elif option == GET_PREDECESSOR:
                    pred = self.predecessors.get_index(0)
                    print(pred)
                    data_resp = pred if pred else self.ref
                elif option == NOTIFY:
                    ip, port = data[1], int(data[2])
                    self.notify(ChordNodeReference(ip, port))
                elif option == CHECK_PREDECESSOR:
                    pass
                elif option == CLOSEST_PRECEDING_FINGER:
                    id = int(data[1])
                    data_resp = self.finger.closest_preceding_finger(id)
                elif option == STORE_KEY:
                    key = data[1]
                    value, version = data[2], int(data[3])
                    rep = True if int(data[4]) == TRUE else False
                    server_response = self.replicator.set(key, Data(value, version), rep)
                elif option == RETRIEVE_KEY:
                    key = data[1]
                    server_response = self.replicator.get(key)
                elif option == DELETE_KEY:
                    key, time = data[1], data[2]
                    rep = True if int(data[3]) == TRUE else False
                    server_response = self.replicator.remove(key, time, rep)
                elif option == PING:
                    server_response = ALIVE
                elif option == PING_LEADER:
                    id, time = int(data[1]), int(data[2])
                    server_response = self.elector.ping_leader(id, time)
                elif option == ELECTION:
                    id, ip, port = int(data[1]), data[2], int(data[3])
                    server_response = self.elector.election(id, ip, port)
                elif option == GET_SUCCESSOR_AND_NOTIFY:
                    index, ip = int(data[1]), data[2]
                    data_resp = self.get_successor_and_notify(index, ip)

                response = None
                if data_resp:
                    response = f'{data_resp.id},{data_resp.ip}'.encode()
                else:
                    response = f'{server_response}'.encode()

                conn.sendall(response)
                conn.close()