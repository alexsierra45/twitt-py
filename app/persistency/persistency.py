import base64
import os
import logging
import grpc

from app.chord.node import ChordNode

logging.basicConfig(level=logging.DEBUG)


def save(node: ChordNode, obj, path):
    full_path = os.path.join("data", path.lower() + ".bin")

    logging.debug(f"Saving file: {full_path}")

    try:
        data = obj.SerializeToString()
    except Exception as e:
        logging.error(f"Error serializing object: {e}")
        return grpc.StatusCode.INTERNAL

    str_data = base64.b64encode(data).decode('utf-8')

    err = node.set_key(full_path, str_data)
    if err:
        logging.error("Error saving file")
        return grpc.StatusCode.INTERNAL

    return None

def load(node: ChordNode, path, obj):
    full_path = os.path.join("data", path.lower() + ".bin")

    logging.debug(f"Loading file: {full_path}")

    data_str, err = node.get_key(full_path)
    if err:
        logging.error(f"Error getting file: {err}")
        return None, grpc.StatusCode.NOT_FOUND

    try:
        data = base64.b64decode(data_str)
        obj.ParseFromString(data)
    except Exception as e:
        logging.error(f"Error decoding object: {e}")
        return None, grpc.StatusCode.INTERNAL

    return obj, None

def delete(node: ChordNode, path):
    full_path = os.path.join("data", path.lower() + ".bin")

    logging.debug(f"Deleting file: {full_path}")

    err = node.remove_key(full_path)
    if err:
        logging.error(f"Error deleting file: {err}")
        return grpc.StatusCode.INTERNAL

    return None

def file_exists(node: ChordNode, path):
    full_path = os.path.join("data", path.lower() + ".bin")

    logging.debug(f"Checking if file exists: {full_path}")

    _, err = node.get_key(full_path)
    if err == grpc.StatusCode.NOT_FOUND:
        logging.debug("File doesn't exist")
        return False, None
    elif err:
        logging.error(f"Error getting file: {err}")
        return False, grpc.StatusCode.INTERNAL

    logging.debug(f"File already exists: {full_path}")
    return True, None