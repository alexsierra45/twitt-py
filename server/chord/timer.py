import logging
import threading
import time
from typing import Dict
from collections import defaultdict

class Timer:
    def __init__(self, node):
        self.node = node

        now = int(time.time())
        
        self.time_counter = now
        self.node_timers: Dict[int, int] = defaultdict(int)
        
        self.node_timers[self.node.id] = now

        self.time_lock = threading.Lock()

    def berkley_algorithm(self) -> int:
        total_time = sum(self.node_timers.values())
        
        return total_time // len(self.node_timers)
    
    def update_time(self):
        logging.info("Update time thread started")
        while not self.node.shutdown_event.is_set():
            with self.time_lock:
                self.time_counter += 1
                self.node_timers[self.node.id] += 1
            time.sleep(1)