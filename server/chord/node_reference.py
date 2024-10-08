import logging
import socket
import traceback
from chord.constants import *
from chord.utils import getShaRepr


# Class to reference a Chord node
class ChordNodeReference:
    def __init__(self, ip: str, port: int = 8001):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port

    # Internal method to send data to the referenced node
    def _send_data(self, op: int, data: str = None) -> bytes:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, int(self.port)))
                s.sendall(f'{op},{data}'.encode('utf-8'))
                return s.recv(1024)
        except Exception as e:
            logging.error(f"Error sending data: {e}, operation: {op}, data: {data}")
            traceback.print_exc()
            return b''

    # Method to find the successor of a given id
    def find_successor(self, id: int) -> 'ChordNodeReference':
        response = self._send_data(FIND_SUCCESSOR, str(id)).decode().split(',')
        return ChordNodeReference(response[1], self.port)

    # Method to find the predecessor of a given id
    def find_predecessor(self, id: int) -> 'ChordNodeReference':
        response = self._send_data(FIND_PREDECESSOR, str(id)).decode().split(',')
        return ChordNodeReference(response[1], self.port)

    # Property to get the successor of the current node
    @property
    def succ(self) -> 'ChordNodeReference':
        response = self._send_data(GET_SUCCESSOR).decode().split(',')
        return ChordNodeReference(response[1], self.port)

    # Property to get the predecessor of the current node
    @property
    def pred(self) -> 'ChordNodeReference':
        response = self._send_data(GET_PREDECESSOR).decode().split(',')
        return ChordNodeReference(response[1], self.port)

    # Method to notify the current node about another node
    def notify(self, node: 'ChordNodeReference'):
        self._send_data(NOTIFY, f'{node.ip},{node.port}')

    # Method to check if the predecessor is alive
    def check_predecessor(self):
        self._send_data(CHECK_PREDECESSOR)

    # Method to find the closest preceding finger of a given id
    def closest_preceding_finger(self, id: int) -> 'ChordNodeReference':
        response = self._send_data(CLOSEST_PRECEDING_FINGER, str(id)).decode().split(',')
        return ChordNodeReference(response[1], self.port)

    # Method to store a key-value pair in the current node
    def store_key(self, key: str, value: str) -> bool:
        response = self._send_data(STORE_KEY, f'{key},{value}').decode()
        return False if response == '' else int(response) == TRUE

    # Method to retrieve a value for a given key from the current node
    def retrieve_key(self, key: str) -> str:
        response = self._send_data(RETRIEVE_KEY, key).decode()
        return response
    
    # Method to delete a key-value pair in the current node
    def delete_key(self, key: str) -> bool: 
        response = self._send_data(DELETE_KEY, key).decode()
        return False if response == '' else int(response) == TRUE
    
    def ping(self) -> bool:
        response = self._send_data(PING).decode()
        return response == ALIVE
    
    def stop_discovering(self):
        self._send_data(STOP_DISCOVERING)
    
    def join(self, node: 'ChordNodeReference') -> bool:
        response = self._send_data(JOIN, f'{node.id},{node.ip}').decode()
        return False if response == '' else int(response) == TRUE
    
    def ping_leader(self, id: int, time: int):
        response = self._send_data(PING_LEADER, f'{id},{time}').decode()
        return int(response)

    def election(self, first_id: int, leader_ip: int, leader_port: int):
        response = self._send_data(ELECTION, f'{first_id},{leader_ip},{leader_port}').decode().split(',')
        return ChordNodeReference(response[0], response[1])

    def __str__(self) -> str:
        return f'{self.id},{self.ip},{self.port}'

    def __repr__(self) -> str:
        return str(self)