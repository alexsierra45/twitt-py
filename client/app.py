import asyncio
import threading
import time
from venv import logger
from app_controller import run
from streamlit.runtime.scriptrunner import add_script_run_ctx
import streamlit as st

from utils import update_servers
from client.grpc_client.grpc_client import get_following, get_user_posts

async def update_storage():
    if 'username' not in st.session_state:
        st.session_state['username'] = None

    user = st.session_state['username']  
    if user:
        token =  st.session_state['token']  
        try:
            await get_user_posts(user, token, request=True)
            await get_following(user, token, request=True)
        except Exception as e:
            logger.error(f"Error updating storage: {str(e)}")
    else:
        logger.info("No storage to update. No user found.")
    


def periodic_task(interval, task_function):
    def wrapper():
        while True:
            task_function()
            time.sleep(interval)
    return wrapper


def run_periodic_tasks():
    tasks = [
        periodic_task(10, update_servers),
        periodic_task(100, lambda: asyncio.run(update_storage()))
    ]
    for task in tasks:
        t = threading.Thread(target=task, daemon=True)
        add_script_run_ctx(t)
        t.start()



async def main():
    run_periodic_tasks()

    await run()


if __name__ == "__main__":
    asyncio.run(main())
