import threading
import concurrent.futures
from collections import deque

import threading
import concurrent.futures

listings = list(range(1, 10))

def parse_listing_element(li):
    print(f"Thread {threading.current_thread().name} processing {li}")
    return li + 100

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(parse_listing_element, li) for li in listings]

    concurrent.futures.wait(futures)

# Collect results
results = [f.result() for f in futures]
print(results)
