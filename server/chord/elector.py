import logging
from chord.timer import TimeRequest, Timer
from chord.node_reference import ChordNodeReference

class Elector:
    def __init__(self, node, timer: Timer) -> None:
        self.node = node
        self.leader: ChordNodeReference = node.leader
        self.timer = timer

    def ping_leader(self, id, time):
        with self.timer.time_lock:

            self.timer.node_timers[id] = time
            self.timer.time_counter = self.timer.berkley_algorithm()
            self.timer.node_timers[self.node.id] = self.timer.time_counter

            return self.timer.time_counter

    def check_leader(self):
        with self.node.leader_lock:
            if self.leader.id == self.id:
                return

            logging.info(f"Check leader: {self.leader.id}")

            with self.timer.time_lock:
                current_time = self.timer.time_counter

            try:
                time_response = self.leader.ping_leader(current_time)
                with self.timer.time_lock:
                    self.timer.time_counter = time_response
                    self.timer.node_timers[self.node.id] = time_response
            except Exception as e:
                logging.error(f"Leader {self.leader.address} failed: {e}")
                self.request_election()

    def request_election(self):
        pass