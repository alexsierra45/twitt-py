import logging
import time
from typing import Dict
from chord.storage import Data, DefaultData, RAMStorage, Storage
from chord.node_reference import ChordNodeReference
from chord.constants import FALSE, TRUE
from chord.dynamic_list import DynamicList
from chord.utils import code_dict, decode_dict, getShaRepr, inbetween
from chord.timer import Timer
from config import SEPARATOR


class Replicator:
    def __init__(self, node, timer: Timer) -> None:
        self.node = node
        self.timer = timer
        self.storage: Storage = RAMStorage() # Dictionary to store key-value pairs

    def get(self, key: str) -> str:
        with self.storage.storage_lock:
            data, error = self.storage.get(key)
            if error:
                data = DefaultData()
            
            return f'{data.value}{SEPARATOR}{data.version}'
        
    def set(self, key: str, data: Data, rep: bool) -> str:
        logging.info(f'Saving key {key}')
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

        ok = node.set_partition(code_dict(new_dict), code_dict(new_version), code_dict(new_removed_dict))
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
                succ: ChordNodeReference = self.node.successors.get_index(i)
                if succ.id == self.node.id:
                    continue
                ok = succ.set_partition(code_dict(new_dict), code_dict(new_version), code_dict(new_removed_dict))
                if not ok:
                    logging.error(f'Error replicating in {succ.ip}')

    def resolve_data(self, dict: Dict[str, str], version: Dict[str, int], removed_dict: Dict[str, int]) -> str:
        logging.info('Resolving data versions')
        print(dict)

        new_dict: Dict[str, Data] = {}
        res_dict_value: Dict[str, str] = {}
        res_dict_version: Dict[str, int] = {}
        res_removed_dict: Dict[str, int] = {}

        with self.storage.storage_lock:
            actual_dict, error = self.storage.get_all()
            if not error:
                return ''
            
            for key, value in dict.items():
                try:
                    data = actual_dict[key]
                except:
                    data = DefaultData()

                if data.version > version[key]:
                    res_dict_value[key] = data.value
                    res_dict_version[key] = data.version
                else:
                    new_dict[key] = Data(value, version[key])

            for key, time in removed_dict.items():
                try:
                    data = actual_dict[key]
                except:
                    data = DefaultData()

                if data.version > time:
                    res_dict_value[key] = data.value
                    res_dict_version[key] = data.version
                else:
                    self.storage.remove(key, time)

            remove, _ = self.storage.get_remove_all()

            for key, data in remove.items():
                time = version[key]

                if data.version > time:
                    res_removed_dict[key] = data.version

            self.storage.set_all(new_dict)

            return f'{code_dict(res_dict_value)}{SEPARATOR}{code_dict(res_dict_version)}{SEPARATOR}{code_dict(res_removed_dict)}'

    def new_predecessor_storage(self):
        with self.node.succ_lock:
            pred: ChordNodeReference = self.node.predecessors.get_index(0)
            pred_pred: ChordNodeReference
            if len(self.node.predecessors) > 1:
                pred_pred = self.node.predecessors.get_index(1)
            else:
                pred_pred = self.node.ref

        if pred.id == pred_pred.id:
            return
        
        logging.info('Delegate predecessor data')

        with self.storage.storage_lock:
            dict, _ = self.storage.get_all()
            remove, _ = self.storage.get_remove_all()

        new_dict: Dict[str, str] = {}
        new_version: Dict[str, int] = {}
        new_removed_dict: Dict[str, int] = {}

        for key, data in dict.items():
            if not inbetween(getShaRepr(key), pred_pred.id, pred.id):
                continue

            new_dict[key] = data.value
            new_version[key] = data.version

        for key, data in remove.items():
            if not inbetween(getShaRepr(key), pred_pred.id, pred.id):
                continue

            new_removed_dict[key] = data.version

        response, ok = pred.resolve_data(code_dict(new_dict), code_dict(new_version), code_dict(new_removed_dict))
        if not ok:
            logging.error(f'Error resolving data in {pred.ip}')
            return
        
        res_dict: Dict[str, str] = decode_dict(response[0])
        res_version: Dict[str, int] = decode_dict(response[1])
        res_removed_dict: Dict[str, int] = decode_dict(response[2])

        new_res_dict: Dict[str, Data] = {}

        for key, value in res_dict.items():
            new_res_dict[key] = Data(value, res_version[key])
        
        with self.storage.storage_lock:
            self.storage.set_all(new_res_dict)
            self.storage.remove_all(res_removed_dict)

    def fix_storage(self):
        while True:
            try:
                logging.info('Fixing storage')

                with self.storage.storage_lock:
                    dict, _ = self.storage.get_all()
                    logging.info(f'Data storage len: {len(dict)}')
                    print(self.storage.storage)

                with self.node.succ_lock:
                    succ_len = len(self.node.successors)

                with self.node.pred_lock:
                    while len(self.node.predecessors) > succ_len:
                        self.node.predecessors.remove_index(len(self.node.predecessors) - 1)
                        if len(self.node.predecessors) == 0:
                            self.node.predecessors.set_index(0, self.node.ref)
                            break

                with self.node.pred_lock:
                    pred: ChordNodeReference = self.node.predecessors.get_index(len(self.node.predecessors) - 1)

                if pred.id != self.node.id:
                    pred_pred = pred.pred

                    if pred_pred.id != self.node.id and pred_pred.id != pred.id:
                        with self.timer.time_lock:
                            time_c = self.timer.time_counter
                        print(pred_pred.id)
                        for key in dict.keys():
                            if inbetween(getShaRepr(key), pred_pred.id, self.node.id):
                                continue

                            self.storage.remove(key, time_c)
            except Exception as e:
                logging.error(f'Error in storage fix: {e}')

            time.sleep(60)