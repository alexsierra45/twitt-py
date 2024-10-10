import logging
from typing import Dict
from chord.storage import Data, DefaultData, RAMStorage, Storage
from chord.node_reference import ChordNodeReference
from chord.constants import FALSE, TRUE
from chord.dynamic_list import DynamicList
from chord.utils import code_dict, getShaRepr, inbetween


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

    def set_partition(self, dict: Dict[str, str], version: Dict[str, int], removed_dict: Dict[str, int]) -> bool:
        new_dict: Dict[str, Data] = {}

        for key in dict.keys():
            new_dict[key] = Data(dict[key], version[key])

        with self.storage.storage_lock:
            try:
                self.storage.set_all(new_dict)
                self.storage.remove_all(removed_dict)
            except:
                return FALSE
            
        return TRUE

    def replicate_all_data(self, node: ChordNodeReference):
        with self.node.pred_lock:
            pred = self.node.predecessors.get_index(0)

        if pred.id == self.node.id:
            return
        
        logging.info(f'Replicate all data in {node.ip}')

        with self.storage.storage_lock:
            dict, _ = self.storage.get_all()
            removed_dict, _ = self.storage.get_remove_all()

        new_dict: Dict[str, str] = {}
        new_version: Dict[str, int] = {}
        new_removed_dict: Dict[str, int] = {}

        for key, data in dict.items():
            if inbetween(getShaRepr(key), pred.id, self.node.id):
                new_dict[key] = data.value
                new_version[key] = data.version

        for key, data in removed_dict.items():
            if inbetween(getShaRepr(key), pred.id, self.node.id):
                new_removed_dict[key] = data.version

        ok = node.set_partition(code_dict(new_dict), code_dict(new_version), code_dict(removed_dict))
        if not ok:
            logging.error(f'Error replicating all data')

    def fail_predecessor_storage(self):
        with self.node.pred_lock:
            pred: ChordNodeReference = self.node.predecessors.get_index(0)

        if pred.id == self.node.id:
            return
        
        logging.info('Absorbe all predecessor data')

        with self.storage.storage_lock:
            dict, _ = self.storage.get_all()
            removed_dict, _ = self.storage.get_remove_all()

        new_dict: Dict[str, str] = {}
        new_version: Dict[str, int] = {}
        new_removed_dict: Dict[str, int] = {}

        for key, data in dict.items():
            if inbetween(getShaRepr(key), pred.id, self.node.id):
                continue

            new_dict[key] = data.value
            new_version[key] = data.version

        for key, data in removed_dict.items():
            if inbetween(getShaRepr(key), pred.id, self.node.id):
                continue
            
            new_removed_dict[key] = data.version

        with self.node.succ_lock:
            for i in range(len(self.node.successors)):
                succ: ChordNodeReference = self.successors.get_index(i)
                ok = succ.set_partition(new_dict, new_version, new_removed_dict)
                if not ok:
                    logging.error(f'Error replicating in {succ.ip}')