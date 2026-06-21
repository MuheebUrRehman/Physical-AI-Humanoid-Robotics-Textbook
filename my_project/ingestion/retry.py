import logging
import time

def handle_api_call_with_retry(api_call_func, *args, max_retries: int = 3, **kwargs):
    last_exception = None
    for attempt in range(max_retries):
        try:
            return api_call_func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt == max_retries - 1:
                logging.error(f"API call failed after {max_retries} attempts: {str(e)}")
                raise
            delay = 1.0 * (2 ** attempt)
            logging.warning(f"API call attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
            time.sleep(delay)
