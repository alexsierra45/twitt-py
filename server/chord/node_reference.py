import logging
import socket
import traceback
from typing import List, Tuple
from chord.constants import *
from chord.utils import getShaRepr
from config import PORT, SEPARATOR
from chord.storage import Data

# Class to reference a Chord node
class ChordNodeReference:
    def __init__(self, ip: str, port: int = PORT):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port

    # Internal method to send data to the referenced node
    def _send_data(self, op: int, data: str = None) -> bytes:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((self.ip, int(self.port)))
                s.sendall(f'{op}{SEPARATOR}{data}'.encode('utf-8'))
                return s.recv(1024)
        except Exception as e:
            logging.error(f"Error sending data to {self.ip}: {e}, operation: {op}, data: {data}")
            # traceback.print_exc()
            return b''

    # Method to find the successor of a given id
    def find_successor(self, id: int) -> 'ChordNodeReference':
        response = self._send_data(FIND_SUCCESSOR, str(id)).decode().split(SEPARATOR)
        return ChordNodeReference(response[1], self.port)

    # Method to find the predecessor of a given id
    def find_predecessor(self, id: int) -> 'ChordNodeReference':
        response = self._send_data(FIND_PREDECESSOR, str(id)).decode().split(SEPARATOR)
        return ChordNodeReference(response[1], self.port)

    # Property to get the successor of the current node
    @property
    def succ(self) -> 'ChordNodeReference':
        response = self._send_data(GET_SUCCESSOR).decode().split(SEPARATOR)
        return ChordNodeReference(response[1], self.port)

    # Property to get the predecessor of the current node
    @property
    def pred(self) -> 'ChordNodeReference':
        response = self._send_data(GET_PREDECESSOR).decode().split(SEPARATOR)
        return ChordNodeReference(response[1], self.port)

    # Method to notify the current node about another node
    def notify(self, node: 'ChordNodeReference'):
        self._send_data(NOTIFY, f'{node.ip}{SEPARATOR}{node.port}')

    # Method to check if the predecessor is alive
    def check_predecessor(self):
        self._send_data(CHECK_PREDECESSOR)

    # Method to find the closest preceding finger of a given id
    def closest_preceding_finger(self, id: int) -> 'ChordNodeReference':
        response = self._send_data(CLOSEST_PRECEDING_FINGER, str(id)).decode().split(SEPARATOR)
        return ChordNodeReference(response[1], self.port)

    # Method to retrieve a value for a given key from the current node
    def retrieve_key(self, key: str) -> Data:
        response = self._send_data(RETRIEVE_KEY, key).decode().split(SEPARATOR)
        return Data(response[0], int(response[1]))
    
    # Method to store a key-value pair in the current node
    def store_key(self, key: str, value: str, version: int, rep: bool = False) -> bool:
        response = self._send_data(STORE_KEY, f'{key}{SEPARATOR}{value}{SEPARATOR}{version}{SEPARATOR}{TRUE if rep else FALSE}').decode()
        return False if response == '' else int(response) == TRUE
    
    # Method to delete a key-value pair in the current node
    def delete_key(self, key: str, time: int, rep: bool = False) -> bool: 
        response = self._send_data(DELETE_KEY, f'{key}{SEPARATOR}{time}{SEPARATOR}{TRUE if rep else FALSE}').decode()
        return False if response == '' else int(response) == TRUE
    
    def ping(self) -> bool:
        response = self._send_data(PING).decode()
        return response == ALIVE
    
    def ping_leader(self, id: int, time: int):
        response = self._send_data(PING_LEADER, f'{id}{SEPARATOR}{time}').decode()
        return int(response)

    def election(self, first_id: int, leader_ip: int, leader_port: int) -> 'ChordNodeReference':
        response = self._send_data(ELECTION, f'{first_id}{SEPARATOR}{leader_ip}{SEPARATOR}{leader_port}').decode().split(SEPARATOR)
        return ChordNodeReference(response[0], response[1])
    
    def get_successor_and_notify(self, index, ip) -> 'ChordNodeReference':
        response = self._send_data(GET_SUCCESSOR_AND_NOTIFY, f'{index}{SEPARATOR}{ip}').decode().split(SEPARATOR)
        return ChordNodeReference(response[1], self.port)
    
    def set_partition(self, dict: str, version: str, remove: str) -> bool:
        response = self._send_data(SET_PARTITION, f'{dict}{SEPARATOR}{version}{SEPARATOR}{remove}').decode()
        return False if response == '' else int(response) == TRUE
    
    def resolve_data(self, dict: str, version: str, remove: str) -> Tuple[List[str], bool]:
        response = self._send_data(RESOLVE_DATA, f'{dict}{SEPARATOR}{version}{SEPARATOR}{remove}').decode().split(SEPARATOR)
        return response, len(response) > 1

    def __str__(self) -> str:
        return f'{self.id},{self.ip},{self.port}'

    def __repr__(self) -> str:
        return str(self)