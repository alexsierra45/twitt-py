import logging
import socket
import time

from chord.node_reference import ChordNodeReference
from chord.constants import ARE_YOU, EMPTY, YES_IM
from config import BROADCAST_LISTEN_PORT, BROADCAST_REQUEST_PORT, SEPARATOR
from chord.elector import Elector
from chord.finger_table import FingerTable

class Discoverer:
    def __init__(self, node, succ_lock, pred_lock, elector: Elector, finger: FingerTable) -> None:
        self.node = node
        self.succ_lock = succ_lock
        self.pred_lock = pred_lock
        self.elector = elector
        self.finger = finger

    def join(self, node_ip, leader_ip):
        node = ChordNodeReference(node_ip)
        leader = ChordNodeReference(leader_ip)
        try:
            with self.succ_lock and self.pred_lock:
                self.node.predecessors.set_index(0, self.node.ref)
                self.node.successors.clear()
                self.node.successors.set_index(0, node.find_successor(self.node.id))
                succ: ChordNodeReference = self.node.successors.get_index(0)
                with self.finger.finger_lock:
                    self.finger.finger[0] = succ
                with self.elector.leader_lock:
                    self.elector.leader = leader
                succ.notify(self.node.ref)
                logging.info(f'Joining node {node.ip}')
                return True
        except Exception as e:
            logging.error(f'Error joining to chord ring: {e}')
            return False

    def send_announcement(self):
        logging.info('Looking for a chord ring via broadcast!!!')
        timeout = 5

        broadcast_addr = ('<broadcast>', int(BROADCAST_LISTEN_PORT))

        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            conn.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            conn.bind(('', int(BROADCAST_REQUEST_PORT)))
        except Exception as e:
            return EMPTY, EMPTY, e

        message = f"{ARE_YOU}{SEPARATOR}{self.node.id}".encode()
        conn.sendto(message, broadcast_addr)

        buffer = bytearray(1024)

        conn.settimeout(2)

        for _ in range(timeout):
            try:
                nn, addr = conn.recvfrom_into(buffer)
                res = buffer[:nn].decode().split(SEPARATOR)
                message = res[0]

                if message == YES_IM and len(res) == 2:
                    ip = addr[0]
                    leader_ip = res[1]
                    logging.info(f"Chord ring discovered in {ip} :)")
                    return ip, leader_ip, None
            except socket.timeout:
                continue
            except Exception as e:
                logging.error("Error receiving message:", e)
                return EMPTY, EMPTY, e

        logging.info("No chord ring was discovered :(")
        return EMPTY, EMPTY, None
    
    def listen_for_announcements(self):
        # Crear un socket UDP para escuchar en el puerto específico
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            conn.bind(('', BROADCAST_LISTEN_PORT))
        except Exception as e:
            logging.error(f"Error running UDP server: {e}")
            return

        buffer = bytearray(1024)

        while True:
            try:
                nn, client_addr = conn.recvfrom_into(buffer)
            except Exception as e:
                logging.error(f"Error reading the buffer: {e}")
                continue

            with self.elector.leader_lock:
                leader_id = self.elector.leader.id

            if leader_id != self.node.id:
                continue 

            res = buffer[:nn].decode().split(SEPARATOR)

            if len(res) != 2:
                continue

            message = res[0]
            id = int(res[1])

            if id == self.node.id:
                continue # Ignorar mensajes del propio nodo

            logging.info(f"Message received from {client_addr}")

            if message == ARE_YOU:
                with self.elector.leader_lock:
                    leader = self.elector.leader

                response = f"{YES_IM}{SEPARATOR}{leader.ip}".encode()
                conn.sendto(response, client_addr)
    
    def create_ring(self):
        logging.info('Create a chord ring')

        with self.pred_lock:
            self.node.predecessors.set_index(0, self.node.ref)
        with self.succ_lock:
            self.node.successors.set_index(0, self.node.ref)
        with self.elector.leader_lock:
            self.elector.leader = self.node.ref

    def create_ring_or_join(self):
        node_ip, leader_ip, error = self.send_announcement()

        if not error and node_ip != EMPTY:
            if not self.join(node_ip, leader_ip):
                self.create_ring()
            return 
        
        self.create_ring()

    def discover_and_join(self):
        while not self.node.shutdown_event.is_set():
            with self.elector.leader_lock:
                leader_id = self.elector.leader.id
            with self.node.succ_lock: 
                succ: ChordNodeReference = self.node.successors.get_index(0)
            with self.node.pred_lock: 
                pred: ChordNodeReference = self.node.predecessors.get_index(0)
            alone = succ.id == pred.id and succ.id == self.node.id

            if leader_id == self.node.id or alone:
                node_ip, leader_ip, error = self.send_announcement()
                if error or node_ip == EMPTY:
                    if error:
                        logging.error(f'Error in broadcast: {error}')
                else:
                    leader = ChordNodeReference(leader_ip)
                    if leader.id > self.node.id:
                        if not self.join(node_ip, leader_ip):
                            logging.error(f'Joining to {node_ip}')
            time.sleep(60)