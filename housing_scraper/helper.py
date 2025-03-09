from typing import Callable, List, Tuple
import concurrent.futures

class ParallelOfficer:
    """Responsible for handling parallelized computation."""

    def __init__(self, max_worker):
        self.max_worker = max_worker
    
    def process_parallel_list(item_list : List, func : Callable, args : Tuple):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(func, i) for i in item_list]

            concurrent.futures.wait(futures)

        return [f.result() for f in futures]


        