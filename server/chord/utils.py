import hashlib
import logging
import time

# Function to hash a string using SHA-1 and return its integer representation
def getShaRepr(data: str):
    return int(hashlib.sha1(data.encode()).hexdigest(), 16)

def repeat(sleep_time, condition: lambda *args: True):
    '''Repeat periodically this function call'''
    def decorator(func):
        def inner(*args, **kwargs):
            while condition(*args):
                func(*args, **kwargs)
                time.sleep(sleep_time)
        return inner
    return decorator

def retry_if_failure(retry_delay: float, attempts: int = 3):
    '''Retry call this funtion awating and give hope to in stabilization'''
    def decorator(func):
        def inner(*args, **kwargs):
            for i in range(attempts):
                try:
                    result = func(*args, **kwargs)
                except BaseException as error:
                    logging.info(f'Retry {i+1}/{attempts} {func.__name__}:  {error}')
                    time.sleep(retry_delay)
                    continue
                if i > 0:
                    logging.info(f'Resolve correctly function: {func.__name__} in attemt {i}')
                return result
            logging.error(f"Can't handle exceptions with stabilization")
            args[0].print_info()
        return inner
    return decorator