import logging
import threading
import time
from chord.node_reference import ChordNodeReference
from chord.utils import inbetween


class FingerTable:
    def __init__(self, node, m = 160) -> None:
        self.node = node
        self.m = m
        self.finger = [self.node.ref] * self.m  # Finger table
        self.next = 0  # Finger table index to fix next
        self.finger_lock = threading.RLock() 

    # Method to find the successor of a given id
    def find_succ(self, id: int) -> 'ChordNodeReference':
        logging.info(f'Find successor for {id}')
        node = self.find_pred(id)  # Find predecessor of id
        
        with self.node.succ_lock:
            if self.node.id == node.id:
                return self.node.successors.get_index(0)
            
        return node.succ  # Return successor of that node
    
    # Method to find the predecessor of a given id
    def find_pred(self, id: int) -> 'ChordNodeReference':
        node = self.node
        first_time = True
        succ: ChordNodeReference = node.successors.get_index(0)
        while not inbetween(id, node.id, succ.id):
            if first_time:
                first_time = False
                node = node.finger.closest_preceding_finger(id)
            else:
                node = node.closest_preceding_finger(id)
        return node.ref if first_time else node
    
    # Method to find the closest preceding finger of a given id
    def closest_preceding_finger(self, id: int) -> ChordNodeReference:
        for i in range(self.m - 1, -1, -1):
            with self.finger_lock:
                if self.finger[i] and inbetween(self.finger[i].id, self.node.id, id):
                    return self.finger[i]
        return self.node.ref
    
    # Fix fingers method to periodically update the finger table
    def fix_fingers(self):
        logging.info('Fix fingers thread started')
        while not self.node.shutdown_event.is_set():
            try:
                self.next += 1
                if self.next >= self.m:
                    self.next = 0

                succ = self.find_succ((self.node.id + 2 ** self.next) % 2 ** self.m)
                logging.info(f'Correspondent finger found at {succ.id}')
                with self.finger_lock:
                    if succ.id == self.node:
                        for i in range(self.next, self.m):
                            self.finger[i] = None
                        self.next = 0
                        continue

                self.finger[self.next] = succ
            except Exception as e:
                logging.error(f"Error in fix fingers thread: {e}")
            time.sleep(10)