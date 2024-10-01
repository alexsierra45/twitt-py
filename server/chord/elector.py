import logging
import threading
import time
from chord.timer import Timer
from chord.node_reference import ChordNodeReference

class Elector:
    def __init__(self, node, timer: Timer) -> None:
        self.node = node
        self.leader: ChordNodeReference = None
        self.leader_lock = threading.RLock()
        
        self.timer = timer

    def ping_leader(self, id: int, time: int):
        with self.timer.time_lock:

            self.timer.node_timers[id] = time
            self.timer.time_counter = self.timer.berkley_algorithm()
            self.timer.node_timers[self.node.id] = self.timer.time_counter

            return self.timer.time_counter

    def check_leader(self):
        while not self.node.shutdown_event.is_set():
            with self.leader_lock:
                if self.leader and self.leader.id != self.node.id:
                    logging.info(f"Check leader: {self.leader.id}")

                    with self.timer.time_lock:
                        current_time = self.timer.time_counter

                    try:
                        time_response = self.leader.ping_leader(self.node.id, current_time)
                        with self.timer.time_lock:
                            self.timer.time_counter = time_response
                            self.timer.node_timers[self.node.id] = time_response
                    except Exception as e:
                        logging.error(f"Leader {self.leader.id} failed: {e}")
                        self.request_election()
            time.sleep(10)

    def election_thread(self):
        logging.info("Election requested thread started")
        while not self.node.shutdown_event.is_set():
            with self.leader_lock:
                leader_id = self.leader.id
            if leader_id == self.node.id:
                self.request_election()
            time.sleep(60)

    def request_election(self):
        with self.node.succ_lock:
            succ: ChordNodeReference = self.node.successors.get_index(0)

        if (self.node.id == succ.id):
            with self.leader_lock:
                self.leader = self.node.ref
            logging.info(f"Node {self.node.id} is now the leader")
            return
        
        logging.info("Elections requested")
        ok = succ.ping()
        if not ok:
            with self.leader_lock:
                self.leader = self.node.ref
            logging.error(f"Failed to connect to successor {succ.id}")
            return
        
        try:
            self.leader = succ.election(self.node.id, self.node.ip, self.node.port)
            logging.info(f"New leader elected: {self.leader.id}")
        except Exception as e:
            with self.leader_lock:
                self.leader = self.node.ref
            logging.error(f"Election failed: {e}")

    def election(self, first_id, leader_ip, leader_port):
        leader = ChordNodeReference(leader_ip, leader_port)
        first_id = first_id

        if self.node.id > leader.id:
            leader = self.node.ref

        with self.node.succ_lock:
            succ: ChordNodeReference = self.node.successors.get_index(0)

        if succ.id == self.node.id or succ.id == first_id:
            with self.leader_lock:
                self.leader = leader

            return f'{leader.ip},{leader.port}'

        ok = succ.ping()
        if not ok:
            logging.info('Failed to connect to successor')
            return None

        try:
            leader = succ.election(first_id, leader.ip, leader.port)
        except Exception as e:
            logging.info(f"Election failed: {e}")
            return None

        with self.leader_lock:
            self.leader = leader

        return f'{leader.ip},{leader.port}'