import logging
from chord.storage import Data, DefaultData, RAMStorage, Storage
from chord.node_reference import ChordNodeReference
from chord.constants import FALSE, TRUE
from chord.dynamic_list import DynamicList


class Replicator:
    def __init__(self, node) -> None:
        self.node = node
        self.storage: Storage = RAMStorage() # Dictionary to store key-value pairs

    def get(self, key: str) -> str:
        with self.storage.storage_lock:
            data, error = self.storage.get(key)
            if error:
                data = DefaultData()
            
            return f'{data.value},{data.version}'
        
    def set(self, key: str, data: Data, rep: bool) -> str:
        with self.storage.storage_lock:
            self.storage.set(key, data)

        with self.node.succ_lock:
            succ: ChordNodeReference = self.node.successors.get_index(0)

        if rep and succ.id != self.node.id:
            try:
                self.set_replicate(key, data)
            except:
                logging.error(f'Error replicating data with key {key} and value {data.value} from {succ.ip}')
                return FALSE

        return TRUE
        
    def set_replicate(self, key: str, data: Data):
        logging.info(f'Replicating key {key}')

        with self.node.succ_lock:
            successors: DynamicList[ChordNodeReference] = self.node.successors

            for i in range(len(successors)):
                try:
                    succ_i = successors.get_index(i)
                    logging.info(f'Set replicate key {key} in {succ_i.ip}')
                    ok = succ_i.store_key(key, data.value, data.version)
                    if not ok:
                        logging.error(f'Error replicating key {key} in successor {i}')
                except:
                    logging.error(f'Error replicating key {key} in successor {i}')

    def remove(self, key: str, time: int, rep: bool) -> bool:
        with self.storage.storage_lock:
            self.storage.remove(key, time)

        with self.node.succ_lock:
            succ: ChordNodeReference = self.node.successors.get_index(0)

        if rep and succ.id != self.node.id:
            try:
                self.remove_replicate(key, time)
            except:
                logging.error(f'Error removing key {key} from {succ.ip}')
                return FALSE

        return TRUE
    
    def remove_replicate(self, key: str, time: int):
        logging.info(f'Removing key {key}')

        with self.node.succ_lock:
            successors: DynamicList[ChordNodeReference] = self.node.successors

            for i in range(len(successors)):
                try:
                    succ_i = successors.get_index(i)
                    logging.info(f'Remove replicate key {key} from {succ_i.ip}')
                    ok = succ_i.delete_key(key, time)
                    if not ok:
                        logging.error(f'Error removing key {key} in successor {i}')
                except:
                    logging.error(f'Error removing key {key} in successor {i}')