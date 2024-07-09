import os

import grpc
from persistency import save, load, file_exists

def exists_user(username):
    path = os.path.join("User", username.lower())
    return file_exists(None, path)

def load_user(username):
    path = os.path.join("User", username.lower())
    user, err = load(None, path, dict)

    if err == grpc.StatusCode.NOT_FOUND:
        return None, grpc.StatusCode.NOT_FOUND
    elif err:
        return None, grpc.StatusCode.INTERNAL

    return user, None

def save_user(user):
    path = os.path.join("User", user["username"].lower())
    err = save(None, user, path)

    if err:
        return grpc.StatusCode.INTERNAL

    return None