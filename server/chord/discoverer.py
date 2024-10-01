import logging
import socket
import threading
import time
import uuid

from chord.node_reference import ChordNodeReference
from chord.constants import ARE_YOU, EMPTY, FALSE, TRUE, YES_IM
from config import BROADCAST_LISTEN_PORT, BROADCAST_REQUEST_PORT, PORT
from chord.elector import Elector
from chord.finger_table import FingerTable

class Discoverer:
    def __init__(self, node, succ_lock, pred_lock, elector: Elector, finger: FingerTable) -> None:
        self.node = node
        self.succ_lock = succ_lock
        self.pred_lock = pred_lock
        self.elector = elector
        self.finger = finger

        self.times = 3
        self.joined = False
        self.node_id = str(uuid.uuid4())  # Unique identifier for this node

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
                # self.joined = True
                # return TRUE
        except Exception as e:
            logging.error(f'Error joining to chord ring: {e}')
            return False
            # return FALSE

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

        message = f"{ARE_YOU};{self.node.id}".encode()
        conn.sendto(message, broadcast_addr)

        buffer = bytearray(1024)

        conn.settimeout(2)

        for _ in range(timeout):
            try:
                nn, addr = conn.recvfrom_into(buffer)
                res = buffer[:nn].decode().split(";")
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

            res = buffer[:nn].decode().split(";")

            if len(res) != 2:
                continue

            message = res[0]
            id = res[1]

            if id == self.node.id:
                continue # Ignorar mensajes del propio nodo

            logging.info(f"Message received from {client_addr}")

            if message == ARE_YOU:
                with self.elector.leader_lock:
                    leader = self.elector.leader

                response = f"{YES_IM};{leader.ip}".encode()
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

    # def send_announcement(self):
    #     # Crear un socket UDP para el envío de broadcast
    #     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
    #         s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Habilitar el modo de broadcast
            
    #         # while True:
    #         #     succ: ChordNodeReference = self.node.successors.get_index(0)
    #         #     if succ.id == self.node.id:
    #         #         self.times = 5
    #         #         self.joined = False

    #         logging.info('Looking for a chord ring via broadcast!!!')
    #         while self.times > 0 and not self.joined:
    #             message = f"{ARE_YOU}:{self.node.ip}:{self.node_id}"
    #             s.sendto(message.encode(), ('<broadcast>', BROADCAST_PORT))  # Enviar el mensaje a la dirección de broadcast
    #             time.sleep(5)
    #             self.times -= 1
    #         if self.joined:
    #             logging.info('Chord ring discovered :)')
    #         else:
    #             logging.info('No chord ring was discovered :(')
    #             self.stop_discovering()

    #             # time.sleep(60)

    # def stop_discovering(self):
    #     self.times = 0
    #     self.joined = True
    #     threading.Thread(target=self.listen_for_announcements, daemon=True).start()  # Start broadcast discover listener

    # def listen_for_announcements(self):
    #     # Crear un socket UDP para escuchar en el puerto específico
    #     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
    #         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilización del puerto
    #         s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #         s.bind(('', BROADCAST_PORT))  # Escuchar en cualquier IP de la red en el puerto de broadcast

    #         while True:
    #             message, addr = s.recvfrom(1024)
    #             if not message:
    #                 continue  # Ignorar mensajes vacíos
    #             if message.decode().startswith("NODE:"):
    #                 ip, unique_id = message.decode().split(":")[1:]
    #                 if unique_id == self.node_id:
    #                     continue  # Ignorar mensajes del propio nodo
    #                 if not self.joined:
    #                     continue
    #                 logging.info(f"Discovered node: {ip}")
    #                 node = ChordNodeReference(ip, PORT)
    #                 if node.join(self.node.ref):
    #                     node.stop_discovering()


    def discover_and_join(self):
        with self.elector.leader_lock:
            leader_id = self.elector.leader.id
        if leader_id == self.node.id:
            node_ip, leader_ip, error = self.send_announcement()
            if error or node_ip == EMPTY:
                if error:
                    logging.error(f'Error in broadcast: {error}')
            else:
                leader = ChordNodeReference(leader_ip)
                if leader.ip > self.node.ip:
                    if not self.join(node_ip, leader_ip):
                        logging.error(f'Joining to {node_ip}')