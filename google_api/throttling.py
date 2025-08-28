import time
import functools
from gspread.exceptions import APIError


def rate_limited_with_retry(delay=1, max_retries=7):
    """Decorator that combines rate limiting on every call with retry logic for API errors.
    
    Args:
        delay (float): Delay between calls in seconds
        max_retries (int): Maximum number of retry attempts for API errors
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay  # Create a local variable that can be modified
            for attempt in range(max_retries + 1):
                time.sleep(current_delay)
                try:
                    return func(*args, **kwargs)
                except APIError as e:
                    if attempt < max_retries:
                        current_delay *= 2  # exponential backoff
                        print(f"!!! Rate limit hit. Retrying in {current_delay:.1f} seconds...")
                    else:
                        # Last attempt failed, raise the error
                        raise e
        return wrapper
    return decorator
