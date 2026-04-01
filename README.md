# Python Sorted Collection Benchmark: List+Bisect vs. SortedList vs. Redis Sorted Set

## 🎯 Objective
The goal of this benchmark is to compare three approaches for maintaining a sorted collection, specifically for scenarios involving timestamps or ordered sequences:
1.  **Standard List + `bisect` module**: Utilizing Python's built-in `list` and the `bisect.insort` / `bisect.bisect_left` functions.
2.  **`SortedList` (from `sortedcontainers`)**: Using a specialized library designed for high-performance sorted collections without sacrificing the simplicity of Python.
3.  **Redis Sorted Set (`ZSET`)**: An out-of-process, network-backed sorted set using `ZADD` for inserts and `ZCOUNT` for rank queries — the Redis equivalent of bisect.

We evaluate performance across varying scales: **1K**, **100K**, **1M**, **10M**, and **100M** elements.

## 🛠️ The Problem
Maintaining a sorted list is a common requirement (e.g., maintaining a timeline of events, priority queues, lookup tables). 
-   **Standard List (`O(N)` Insert)**: Inserting an element into a sorted list requires finding the position (`O(log N)` search) and then shifting all subsequent elements (`O(N)` move). As $N$ grows to millions, the cost of shifting becomes prohibitive.
-   **SortedList (`O(√N)` Insert)**: The `sortedcontainers` library uses a segmented list approach. Instead of one massive array, it maintains many smaller sub-lists. This reduces the number of elements that need to be shifted, dramatically improving insertion speeds at scale.
-   **Redis Sorted Set (`O(log N)` Insert + network RTT)**: Redis internally uses a skip list for its sorted sets, giving `O(log N)` insert and `O(log N)` rank queries. The downside is every operation crosses a network socket, adding a fixed ~0.1 ms round-trip overhead regardless of data size. Tested only up to 1M elements due to local memory/time constraints.

---

## 📊 Benchmark Results

Running on **macOS (Arm64)** with Python 3.14. Redis 7.x on localhost.

| Size (N) | Method | Bulk Build (s) | Insert Avg (µs) | Search Avg (µs) |
| :--- | :--- | :--- | :--- | :--- |
| **1K** | List+Bisect | 0.000321 | 0.61 | 0.38 |
| | SortedList | 0.000322 | 1.04 | 0.54 |
| | Redis ZSet | 0.009631 | 115.60 | 91.72 |
| **100K** | List+Bisect | 0.030940 | 30.96 | 0.68 |
| | SortedList | 0.030989 | 1.63 | 1.47 |
| | Redis ZSet | 0.684063 | 120.37 | 86.00 |
| **1M** | List+Bisect | 0.390949 | 326.25 | 1.42 |
| | SortedList | 0.411687 | 3.39 | 3.04 |
| | Redis ZSet | 7.195692 | 104.50 | 98.70 |
| **10M** | List+Bisect | 4.020966 | 2,846.78 | 2.62 |
| | SortedList | 4.354274 | 4.72 | 10.06 |
| | Redis ZSet | 79.446143 | 97.73 | 93.76 |
| **100M** | List+Bisect | 50.565074 | 50,936.79 | 59.57 |
| | SortedList | 69.677029 | 26.35 | 621.94 |
| | Redis ZSet | SKIPPED (>10M) | — | — |

> Redis ZSet is skipped at 100M because storing 100M members locally exhausts practical RAM (~17GB needed) and bulk-load time (~800s estimated).

---

## 💡 Conclusion & Recommendations

### 1. Scaling Bottleneck: The "Insertion Wall"
The data confirms that `List+Bisect` hits a performance wall at 1M+ elements.
- At **10M elements**, `SortedList` insert (0.005 ms) is **~603× faster** than `List+Bisect` (2.85 ms).
- At **100M elements**, `SortedList` is **~1935× faster** than `List+Bisect` at inserting new data (0.026 ms vs 50.9 ms per insert).
- If your application involves a continuous stream of data (like logging or order books), `SortedList` is mandatory at scale.

### 2. The Network Tax of Redis
Redis sorted sets pay a fixed per-operation network cost (~0.09–0.12 ms round-trip) regardless of data size.
- At **1,000 elements**: Redis insert is ~190× slower than `List+Bisect` and ~111× slower than `SortedList`.
- At **10,000,000 elements**: Redis insert (0.098 ms) is ~29× faster than `List+Bisect` (2.85 ms) but still **~21× slower** than `SortedList` (0.005 ms).
- Redis's `O(log N)` skip-list insert beats `List+Bisect` somewhere around 1M–10M elements, but is always dominated by `SortedList` for pure in-process throughput.

### 3. The Search Paradox
`bisect.bisect_left` on a contiguous C array remains the fastest search at every scale.
- At **10M**: `List+Bisect` search (2.6 µs) is ~3.8× faster than `SortedList` (10 µs) and ~36× faster than Redis (94 µs).
- Redis search latency is flat (~0.09–0.10 ms) because it is network-bound, not algorithm-bound.

### 4. Bulk Loading
- `list.sort()` and `SortedList(data)` are neck-and-neck at all sizes up to 10M.
- At 100M, `list.sort()` (50.6 s) is 37% faster than `SortedList` (69.7 s).
- Redis bulk load via pipelined `ZADD` scales linearly: 0.68s (100k) → 7.2s (1M) → 79.4s (10M).

### 🚀 Final Verdict

| Use case | Best choice |
| :--- | :--- |
| Mostly static, read-heavy list | **List+Bisect** (fastest search, lowest memory) |
| High insert rate, large N (>100k) | **SortedList** (best insert throughput by far) |
| Shared across multiple processes/services | **Redis ZSet** (the only option; accept ~0.1 ms/op latency) |
| Persistence, pub/sub, TTL on data | **Redis ZSet** |
| Purely in-process, any size | Never Redis (network overhead always dominates) |

---

## 🚀 How to Run
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start Redis (required for Redis ZSet benchmark):
   ```bash
   brew services start redis
   ```
4. Run the benchmark:
   ```bash
   # All sizes (1k, 100k, 1M, 10M, 100M)
   python3 benchmark.py

   # Specific sizes only
   python3 benchmark.py --sizes 10000000
   python3 benchmark.py --sizes 1000000 10000000

   # Override insert/search operation count
   python3 benchmark.py --sizes 10000000 --insert-count 50
   ```
