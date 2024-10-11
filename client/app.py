import asyncio
from venv import logger
from app_controller import run

# def periodic_task(interval, task_function):
#     def wrapper():
#         while True:
#             task_function()
#             time.sleep(interval)
#     return wrapper


# def run_periodic_tasks():
#     tasks = [
#         periodic_task(10, update_server),
#         periodic_task(100, lambda: asyncio.run(update_storage()))
#     ]
#     for task in tasks:
#         t = threading.Thread(target=task, daemon=True)
#         add_script_run_ctx(t)
#         t.start()



async def main():
    # run_periodic_tasks()

    await run()


if __name__ == "__main__":
    asyncio.run(main())
