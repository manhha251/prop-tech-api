import concurrent.futures
from more_itertools import grouper

process_pool = 20


def list_multiprocess(function, items):
    # executor = concurrent.futures.ProcessPoolExecutor(process_pool)
    # futures = [executor.submit(function, group) for group in grouper(items, process_pool)]
    # concurrent.futures.wait(futures)
    with concurrent.futures.ProcessPoolExecutor(max_workers=process_pool) as executor:
        futures = executor.map(function, items)
        return futures
