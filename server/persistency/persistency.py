import base64
# import os
import logging
import grpc

from chord.node import ChordNode

logging.basicConfig(level=logging.DEBUG)

# full_path = os.path.join("data", path.lower() + ".bin")

def is_empty(data: str):
    return data == ''

def save(node: ChordNode, obj, path):
    logging.debug(f"Saving file: {path}")

    try:
        data = obj.SerializeToString()
    except Exception as e:
        logging.error(f"Error serializing object: {e}")
        return grpc.StatusCode.INTERNAL

    str_data = base64.b64encode(data).decode('utf-8')

    ok = node.set_key(path, str_data)
    if not ok:
        logging.error("Error saving file")
        return grpc.StatusCode.INTERNAL
    return None

def load(node: ChordNode, path, obj):
    logging.debug(f"Loading file: {path}")

    data_str = node.get_key(path)
    if is_empty(data_str):
        logging.error(f"Error getting file")
        return None, grpc.StatusCode.NOT_FOUND

    try:
        data = base64.b64decode(data_str)
        obj.ParseFromString(data)
    except Exception as e:
        logging.error(f"Error decoding object: {e}")
        return None, grpc.StatusCode.INTERNAL

    return obj, None

def delete(node: ChordNode, path):
    logging.debug(f"Deleting file: {path}")

    ok = node.remove_key(path)
    if not ok:
        logging.error(f"Error deleting file")
        return grpc.StatusCode.INTERNAL

    return None

def file_exists(node: ChordNode, path):
    logging.debug(f"Checking if file exists: {path}")

    exists = not is_empty(node.get_key(path))
    if not exists:
        logging.debug("File doesn't exist")
        return False, None
    # elif err:
    #     logging.error(f"Error getting file: {err}")
    #     return False, grpc.StatusCode.INTERNAL

    logging.debug(f"File already exists: {path}")
    return True, None