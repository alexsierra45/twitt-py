
import os
import shutil
from venv import logger
import aiofiles
import pickle
from filelock import FileLock
import streamlit as st

class Storage:
    memory_cache = {}

    @staticmethod
    def store(key, value):
        st.session_state[key] = value

    @staticmethod
    def get(key, default=None):
        return st.session_state.get(key, default)

    @staticmethod
    def delete(key):
        if st.session_state.get(key):
            del st.session_state[key]

    @staticmethod
    async def async_disk_store(key, value):
        user_path = os.path.expanduser('~')
        folder_path = f'{user_path}/.socialnetwork'
        file_path = f'{folder_path}/{key}.txt'
        lock_path = f"{file_path}.lock"

        # Guardar en la caché de memoria primero
        Storage.memory_cache[key] = value

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Bloquear solo durante la escritura en disco
        lock = FileLock(lock_path)
        with lock:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(pickle.dumps(value))

    @staticmethod
    async def async_disk_get(key, default=None):
        # Intentar recuperar primero de la caché en memoria
        if key in Storage.memory_cache:
            return Storage.memory_cache[key]

        user_path = os.path.expanduser('~')
        file_path = f'{user_path}/.socialnetwork/{key}.txt'
        lock_path = f"{file_path}.lock"

        if not os.path.exists(file_path):
            return default

        # Bloqueo en caso de acceso a disco
        lock = FileLock(lock_path)
        with lock:
            async with aiofiles.open(file_path, 'rb') as f:
                try:
                    data = await f.read()
                    result = pickle.loads(data)
                    Storage.memory_cache[key] = result  # Actualizar la caché en memoria
                    return result
                except (EOFError, pickle.UnpicklingError):
                    return default
                
    @staticmethod
    async def async_disk_delete(key):
        user_path = os.path.expanduser('~')
        path = f'{user_path}/.socialnetwork/{key}.txt'
        if os.path.exists(path):
            os.remove(path)

    @staticmethod
    def clear():
        server = Storage.get('server', default='localhost')
        st.session_state.clear()
        Storage.store('server', server)
        
        Storage.memory_cache = {}

        # remove all files at folder_path with shutil.rmtree
        user_path = os.path.expanduser('~')
        folder_path = f'{user_path}/.socialnetwork'

        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)


