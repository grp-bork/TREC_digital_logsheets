import time
import random
import functools
from gspread.exceptions import APIError


def rate_limited_retry(max_retries=7, base_delay=2.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for _ in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except APIError as e:
                    if e.response.status_code == 429:
                        print(f"Rate limit hit. Retrying in {delay:.1f} seconds...")
                        time.sleep(delay + random.uniform(0, 0.5))  # add jitter
                        delay *= 2  # exponential backoff
                    else:
                        raise
            raise Exception("Exceeded retry limit due to repeated rate limit errors.")
        return wrapper
    return decorator
