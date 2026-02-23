# Python Sorted Collection Benchmark: List+Bisect vs. SortedList

## 🎯 Objective
The goal of this benchmark is to compare two common approaches for maintaining a sorted collection in Python, specifically for scenarios involving timestamps or ordered sequences:
1.  **Standard List + `bisect` module**: Utilizing Python's built-in `list` and the `bisect.insort` / `bisect.bisect_left` functions.
2.  **`SortedList` (from `sortedcontainers`)**: Using a specialized library designed for high-performance sorted collections without sacrificing the simplicity of Python.

We evaluate performance across varying scales: **1,000**, **100,000**, **1,000,000**, and **100,000,000** elements.

## 🛠️ The Problem
Maintaining a sorted list is a common requirement (e.g., maintaining a timeline of events, priority queues, lookup tables). 
-   **Standard List (`O(N)` Insert)**: Inserting an element into a sorted list requires finding the position (`O(log N)` search) and then shifting all subsequent elements (`O(N)` move). As $N$ grows to millions, the cost of shifting becomes prohibitive.
-   **SortedList (`O(√N)` Insert)**: The `sortedcontainers` library uses a segmented list approach. Instead of one massive array, it maintains many smaller sub-lists. This reduces the number of elements that need to be shifted, dramatically improving insertion speeds at scale.

---

## 📊 Benchmark Results

Running on **macOS (Arm64)** with Python 3.

| Size (N) | Method | Bulk Build (s) | Insertion Avg (s) | Search Avg (s) |
| :--- | :--- | :--- | :--- | :--- |
| **1,000** | List+Bisect | 0.0003 | 0.00000063 | 0.00000041 |
| | SortedList | 0.0003 | 0.00000093 | 0.00000052 |
| **100,000** | List+Bisect | 0.0322 | 0.00002460 | 0.00000069 |
| | SortedList | 0.0323 | 0.00000186 | 0.00000170 |
| **1,000,000** | List+Bisect | 0.3965 | 0.00038177 | 0.00000190 |
| | SortedList | 0.4089 | 0.00000388 | 0.00000330 |
| **100,000,000**| List+Bisect | 56.2217 | 0.04223008 | 0.00006430 |
| | SortedList | 112.6936 | 0.00012616 | 0.00065628 |

---

## 💡 Conclusion & Recommendations

### 1. Scaling Bottleneck: The "Insertion Wall"
The data shows that `List+Bisect` hits a performance wall at 1M+ elements.
- At **100M elements**, `SortedList` is **~335 times faster** than at inserting new data.
- If your application involves continuous stream of data (like logging or order books), `SortedList` is mandatory at scale.

### 2. The Search Paradox
Interestingly, **Search (`bisect_left`) is significantly faster on a standard list**.
- `bisect.bisect_left` on a standard list is **~10x faster** than `SortedList` at the 100M mark.
- This is because a standard list is a single contiguous block of memory in C, allowing for extremely efficient pointer arithmetic and cache-friendly access. `SortedList` has to navigate multiple layers of Python objects.

### 3. Memory & Initialization
- **Bulk Loading**: `list.sort()` is nearly **2x faster** than initializing a `SortedList` for 100M elements.
- **Memory**: `SortedList` has higher memory overhead due to its internal tree-like structure of sub-lists.

### 🚀 Final Verdict
- **Use `SortedList`** if your primary operation is **inserting/deleting** elements while maintaining order in a list larger than 100,000 items.
- **Use `list + bisect`** if your list is **mostly static** (read-heavy) or contains fewer than 10,000 items where the overhead of `SortedList` outweighs its benefits.

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
3. Run the benchmark:
   ```bash
   python3 benchmark.py
   ```
