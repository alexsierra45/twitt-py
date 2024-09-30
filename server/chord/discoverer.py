import logging
import socket
import threading
import time
import uuid

from chord.node_reference import ChordNodeReference
from chord.constants import FALSE, TRUE
from config import BROADCAST_PORT

class Discoverer:
    def __init__(self, node, succ_lock, pred_lock) -> None:
        self.node = node
        self.succ_lock = succ_lock
        self.pred_lock = pred_lock
        self.times = 3
        self.joined = False
        self.node_id = str(uuid.uuid4())  # Unique identifier for this node

        threading.Thread(target=self.send_announcement, daemon=True).start()  # Start broadcast discover sender
        # threading.Thread(target=self.listen_for_announcements, daemon=True).start()  # Start broadcast discover listener

    def send_announcement(self):
        # Crear un socket UDP para el envío de broadcast
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Habilitar el modo de broadcast
            
            # while True:
            #     succ: ChordNodeReference = self.node.successors.get_index(0)
            #     if succ.id == self.node.id:
            #         self.times = 5
            #         self.joined = False

            logging.info('Looking for a chord ring via broadcast!!!')
            while self.times > 0 and not self.joined:
                message = f"NODE:{self.node.ip}:{self.node_id}"
                s.sendto(message.encode(), ('<broadcast>', BROADCAST_PORT))  # Enviar el mensaje a la dirección de broadcast
                time.sleep(5)
                self.times -= 1
            if self.joined:
                logging.info('Chord ring discovered :)')
            else:
                logging.info('No chord ring was discovered :(')
                self.stop_discovering()

                # time.sleep(60)

    def stop_discovering(self):
        self.times = 0
        self.joined = True
        threading.Thread(target=self.listen_for_announcements, daemon=True).start()  # Start broadcast discover listener

    def listen_for_announcements(self):
        # Crear un socket UDP para escuchar en el puerto específico
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilización del puerto
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.bind(('', BROADCAST_PORT))  # Escuchar en cualquier IP de la red en el puerto de broadcast

            while True:
                message, addr = s.recvfrom(1024)
                if not message:
                    continue  # Ignorar mensajes vacíos
                if message.decode().startswith("NODE:"):
                    ip, unique_id = message.decode().split(":")[1:]
                    if unique_id == self.node_id:
                        continue  # Ignorar mensajes del propio nodo
                    if not self.joined:
                        continue
                    logging.info(f"Discovered node: {ip}")
                    node = ChordNodeReference(ip, self.node.port)
                    if node.join(self.node.ref):
                        node.stop_discovering()
        
    def join(self, node: 'ChordNodeReference'):
        try:
            with self.succ_lock and self.pred_lock:
                self.node.predecessors.set_index(0, self.node.ref)
                self.node.successors.clear()
                self.node.successors.set_index(0, node.find_successor(self.node.id))
                succ: ChordNodeReference = self.node.successors.get_index(0)
                succ.notify(self.node.ref)
                logging.info(f'Joining node {node.ip}')
                self.joined = True
                return TRUE
        except Exception as e:
            logging.error(f'Error joining to chord ring: {e}')
            return FALSE