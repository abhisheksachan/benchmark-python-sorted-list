
import time
import bisect
import random
from sortedcontainers import SortedList
import sys
import gc

def benchmark_list_bisect(size, insert_count=100):
    print(f"  Benchmarking List+Bisect for size {size:,}...")
    # Bulk loading
    start_time = time.perf_counter()
    data = [random.randint(0, size * 10) for _ in range(size)]
    data.sort()
    bulk_time = time.perf_counter() - start_time
    
    # Inserting
    start_time = time.perf_counter()
    for _ in range(insert_count):
        val = random.randint(0, size * 10)
        bisect.insort(data, val)
    insert_time = (time.perf_counter() - start_time) / insert_count
    
    # Searching
    start_time = time.perf_counter()
    for _ in range(insert_count):
        val = random.randint(0, size * 10)
        _ = bisect.bisect_left(data, val)
    search_time = (time.perf_counter() - start_time) / insert_count
    
    # Clean up
    del data
    gc.collect()
    
    return bulk_time, insert_time, search_time

def benchmark_sorted_list(size, insert_count=100):
    print(f"  Benchmarking SortedList for size {size:,}...")
    # Bulk loading
    start_time = time.perf_counter()
    temp_data = [random.randint(0, size * 10) for _ in range(size)]
    sl = SortedList(temp_data)
    bulk_time = time.perf_counter() - start_time
    del temp_data
    gc.collect()
    
    # Inserting
    start_time = time.perf_counter()
    for _ in range(insert_count):
        val = random.randint(0, size * 10)
        sl.add(val)
    insert_time = (time.perf_counter() - start_time) / insert_count
    
    # Searching
    start_time = time.perf_counter()
    for _ in range(insert_count):
        val = random.randint(0, size * 10)
        _ = sl.bisect_left(val)
    search_time = (time.perf_counter() - start_time) / insert_count
    
    # Clean up
    del sl
    gc.collect()

    return bulk_time, insert_time, search_time

def main():
    # User requested: 1k, 100k, 1M, 100M
    sizes = [1_000, 100_000, 1_000_000, 100_000_000]
    results = []

    print(f"{'Size':>12} | {'Method':>15} | {'Bulk Build (s)':>15} | {'Inst Avg (s)':>12} | {'Srch Avg (s)':>12}")
    print("-" * 85)

    for size in sizes:
        # For 100M, we might need to skip List+Bisect insertion if it's too slow
        # but the user asked for comparison. I'll attempt with a very small insert count for 100M.
        ins_count = 100 if size < 100_000_000 else 10 # Only 10 inserts for 100M List to avoid long hang
        
        try:
            l_bulk, l_ins, l_search = benchmark_list_bisect(size, ins_count)
            print(f"{size:12,d} | {'List+Bisect':>15} | {l_bulk:15.6f} | {l_ins:12.8f} | {l_search:12.8f}")
            results.append((size, 'List+Bisect', l_bulk, l_ins, l_search))
        except MemoryError:
            print(f"{size:12,d} | {'List+Bisect':>15} | {'MEM ERROR':>15} | {'-':>12} | {'-':>12}")

        try:
            sl_bulk, sl_ins, sl_search = benchmark_sorted_list(size, ins_count)
            print(f"{size:12,d} | {'SortedList':>15} | {sl_bulk:15.6f} | {sl_ins:12.8f} | {sl_search:12.8f}")
            results.append((size, 'SortedList', sl_bulk, sl_ins, sl_search))
        except MemoryError:
            print(f"{size:12,d} | {'SortedList':>15} | {'MEM ERROR':>15} | {'-':>12} | {'-':>12}")
            
        print("-" * 85)

    # Save results to file for later
    with open("results.csv", "w") as f:
        f.write("Size,Method,BulkTime,InsertTime,SearchTime\n")
        for r in results:
            f.write(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]}\n")

if __name__ == "__main__":
    main()
