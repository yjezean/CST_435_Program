# Parallel Computing vs Distributed Computing: Performance Trade-offs Explained

## Table of Contents

1. [The Fundamental Question](#the-fundamental-question)
2. [Parallel Computing Explained](#parallel-computing-explained)
3. [Distributed Computing Explained](#distributed-computing-explained)
4. [Why Distributed Can Be Slower](#why-distributed-can-be-slower)
5. [When Distributed Is Beneficial](#when-distributed-is-beneficial)
6. [Amdahl's Law and Communication Overhead](#amdahls-law-and-communication-overhead)
7. [Your Pipeline: Local vs Distributed](#your-pipeline-local-vs-distributed)
8. [Real-World Examples](#real-world-examples)
9. [Conclusion](#conclusion)

---

## The Fundamental Question

**"Why would using containers on another machine make performance WORSE? Shouldn't distributed computing be more efficient?"**

This is an excellent question that highlights a common misconception. The answer is: **It depends on the workload.**

**Key Insight:** Distributed computing doesn't automatically make things faster. It trades **computation time** for **communication overhead**. Whether this trade-off is beneficial depends on:

1. **Communication cost** vs **Computation time**
2. **Network latency** vs **Processing time**
3. **Data size** being transmitted
4. **Parallelizability** of the task

---

## Parallel Computing Explained

### Definition

**Parallel Computing** = Multiple processors/cores working on different parts of the same problem **simultaneously**, typically **within the same machine**.

### Characteristics

- **Same Memory Space**: Processes share memory (or can access it very quickly)
- **Low Latency**: Communication between threads/processes is **nanoseconds to microseconds**
- **High Bandwidth**: Memory bandwidth is **extremely high** (GB/s)
- **Synchronization**: Fast locks, barriers, shared memory
- **Overhead**: Minimal - context switching, memory access

### Examples

```python
# Example: Parallel processing on same machine
from concurrent.futures import ThreadPoolExecutor

# All workers on same machine, same memory
with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(process_service, tasks)
    # Communication: ~0.1 microseconds via shared memory
```

### Performance Characteristics

| Aspect                      | Performance             |
| --------------------------- | ----------------------- |
| Inter-process communication | ~0.1-1 microseconds     |
| Memory access               | ~50-100 nanoseconds     |
| Bandwidth                   | 10-50 GB/s              |
| Synchronization             | Very fast (nanoseconds) |

**Key Point:** Communication is **nearly instantaneous** compared to computation.

---

## Distributed Computing Explained

### Definition

**Distributed Computing** = Multiple machines working together, each with its own memory and processing units, communicating over a **network**.

### Characteristics

- **Separate Memory**: Each machine has isolated memory
- **Network Communication**: Data must travel over network (LAN or WAN)
- **Higher Latency**: Communication is **milliseconds** (1000x slower than local)
- **Lower Bandwidth**: Network bandwidth is **MB/s** (100-1000x lower than memory)
- **Synchronization**: Network calls, timeouts, failures
- **Overhead**: Serialization, network stack, protocol layers

### Examples

```python
# Example: Distributed processing across machines
import rpyc

# Service on Machine A
conn = rpyc.connect('192.168.1.105', 50052)  # Machine B
result = conn.root.process_service(message)
# Communication: ~1-10 milliseconds over network
```

### Performance Characteristics

| Aspect                  | Performance           |
| ----------------------- | --------------------- |
| Network latency (LAN)   | ~0.5-5 milliseconds   |
| Network latency (WAN)   | ~10-100+ milliseconds |
| Bandwidth (LAN)         | 100-1000 MB/s         |
| Serialization overhead  | Additional 1-10ms     |
| Total overhead per call | 2-20ms minimum        |

**Key Point:** Communication is **orders of magnitude slower** than local memory access.

---

## Why Distributed Can Be Slower

### The Communication Overhead Problem

When you distribute services, you **replace fast local communication with slow network communication**.

#### Scenario: Processing 100ms of work

**Local/Parallel (Same Machine):**

```
Service A (processes) → Shared Memory → Service B
Time: 100ms processing + 0.001ms communication = ~100ms total
```

**Distributed (Different Machines):**

```
Service A → Serialize (2ms) → Network (1ms) → Deserialize (2ms) → Service B
Service B → Process (100ms) → Serialize (2ms) → Network (1ms) → Deserialize (2ms) → Service A
Time: 100ms processing + 10ms communication = ~110ms total (10% slower!)
```

### Overhead Breakdown

For each network call, you pay:

1. **Serialization**: Convert Python objects to bytes

   - RPC (pickle): ~2-5ms for typical data
   - gRPC (protobuf): ~0.5-2ms (faster!)

2. **Network Transmission**: Send data over network

   - Local network (LAN): ~0.5-2ms
   - Cross-network: ~5-50ms
   - Internet: ~50-200ms

3. **Deserialization**: Convert bytes back to objects

   - RPC: ~2-5ms
   - gRPC: ~0.5-2ms

4. **Protocol Overhead**: TCP/IP, HTTP/2, etc.
   - ~0.5-1ms per message

**Total Overhead Per Call:**

- RPC on LAN: ~5-13ms
- gRPC on LAN: ~2-6ms

### When Overhead Dominates

If your service processing time is **shorter** than the network overhead, distribution **hurts performance**:

| Processing Time | Network Overhead | Result                         |
| --------------- | ---------------- | ------------------------------ |
| 10ms            | 5ms              | **50% slower!** (15ms vs 10ms) |
| 50ms            | 5ms              | 10% slower (55ms vs 50ms)      |
| 200ms           | 5ms              | 2.5% slower (205ms vs 200ms)   |
| 1000ms          | 5ms              | 0.5% slower (1005ms vs 1000ms) |

**Rule of Thumb:** Network overhead must be **< 10%** of processing time for distributed to be beneficial.

---

## When Distributed IS Beneficial

Distributed computing shines when:

### 1. **Long-Running Tasks**

When computation time **far exceeds** communication overhead:

```
Processing: 5000ms (5 seconds)
Network overhead: 10ms
Benefit: Almost negligible overhead (0.2%)
```

### 2. **True Parallelism with Resource Constraints**

When you **need more resources** than one machine can provide:

```
Scenario: Processing 1000 large images
- One machine: 10 cores → 1000s sequential processing
- Ten machines: 100 cores → 100s parallel processing
- Network overhead: 50ms per image × 10 calls = 500ms
- Total: 100s + 0.5s = 100.5s (99.5% faster!)
```

### 3. **Independent Tasks**

When tasks don't need frequent communication:

```
Scenario: Analyzing independent documents
- Each machine processes its own documents
- No communication needed until final merge
- Perfect for distribution!
```

### 4. **Geographic Distribution**

When data/results need to be closer to users:

```
Scenario: Content delivery network (CDN)
- Distribute servers globally
- Serve content from nearest server
- Network latency to user is reduced
```

### 5. **Fault Tolerance and Availability**

When you need redundancy and reliability:

```
Scenario: Critical services
- Multiple machines can handle requests
- If one fails, others continue
- Network overhead is worth it for reliability
```

---

## Amdahl's Law and Communication Overhead

### Amdahl's Law (Traditional)

**Speedup = 1 / [(1-P) + P/N]**

Where:

- P = fraction of program that can be parallelized
- N = number of processors

**Example:** If 90% can be parallelized with 10 processors:

- Speedup = 1 / [(1-0.9) + 0.9/10] = 1 / [0.1 + 0.09] = **5.26x**

### Amdahl's Law with Communication Overhead

**Speedup = 1 / [(1-P) + P/N + C×N]**

Where:

- C = communication overhead factor
- N = number of processors/machines

**Example:** Same 90% parallelization, 10 machines, but 5ms communication overhead per call:

- Without overhead: 5.26x speedup
- With 5ms overhead (on 100ms task): C = 0.05
- Speedup = 1 / [0.1 + 0.09 + 0.05×10] = 1 / 0.69 = **1.45x**

**The overhead can severely limit speedup!**

### Why This Matters

As you add more machines:

- **Computation scales**: More processors = more parallel work
- **Communication scales**: More machines = more network calls = more overhead
- **At some point**: Communication overhead **exceeds** computation benefit

---

## Your Pipeline: Local vs Distributed

Let's analyze your specific pipeline:

### Current Pipeline Structure

```
Main → A (200ms) → B (150ms) → C (Hub)
                              ├─→ C1 (150ms)
                              ├─→ C2 (200ms)
                              ├─→ C3 (300ms) [longest]
                              └─→ C4 (100ms)
        → D (50ms)
Total: ~200 + 150 + max(150,200,300,100) + 50 = ~750ms (local)
```

### Scenario 1: All Services Local (Current)

```
Processing Time: ~750ms
Communication: ~0.001ms (shared memory)
Total: ~750ms
```

### Scenario 2: Distributed - All Services on Different Machines

**Sequential Calls:**

- A → B: 200ms + 5ms network = 205ms
- B → C: 150ms + 5ms network = 155ms
- C → D: 50ms + 5ms network = 55ms

**Parallel Calls (from C):**

- C → C1: 150ms + 5ms network = 155ms
- C → C2: 200ms + 5ms network = 205ms
- C → C3: 300ms + 5ms network = 305ms
- C → C4: 100ms + 5ms network = 105ms
- Max: 305ms

**Total:** 205 + 155 + 305 + 55 = **~720ms** (but this assumes perfect parallelization)

**Reality Check:**

- Network calls add latency even to parallel services
- Total: ~750ms + network overhead = **~770-800ms**

### Scenario 3: Your Actual Distribution (Recommended)

**Windows:**

- Main → A (local, 200ms)
- A → B (network, 150ms + 5ms = 155ms)

**Linux:**

- B → C (local, ~0ms coordination)
- C → C1 (local, 150ms)
- C → C2 (network, 200ms + 5ms = 205ms)
- C → C3 (local, 300ms)
- C → C4 (network, 100ms + 5ms = 105ms)
- C → D (local, 50ms)
- D → Main (network response, 5ms)

**Total:** 200 + 155 + max(150, 205, 300, 105) + 50 + 5 = **~710ms**

### Why Distributed Might Still Be Slower Here

1. **Short Processing Times**: Your services process in 100-300ms
2. **Network Overhead**: 5-10ms per call adds up
3. **Sequential Dependencies**: A→B→C→D must wait for each step
4. **Multiple Network Calls**: Even with parallel services, you have network calls

**Result:**

- Local: ~750ms
- Distributed: ~710-800ms (can be slightly faster if network is very fast, or slower if network has latency)

### When Distribution Would Help Your Pipeline

Distribution would be beneficial if:

1. **Services Process Longer**: If each service took 2-5 seconds instead of 0.1-0.3 seconds

   - Overhead becomes negligible percentage

2. **Heavy CPU Usage**: If services are CPU-bound and you need more cores

   - Multiple machines = more total CPU cores

3. **Independent Processing**: If services didn't need to wait for each other

   - Pipeline creates dependencies that limit parallelism

4. **Large Data Processing**: If you're processing huge datasets
   - Network overhead becomes small relative to data processing time

---

## Real-World Examples

### Example 1: Video Rendering (Distributed Wins)

**Task:** Render 1000 video frames

**Local (1 machine, 8 cores):**

- 1000 frames ÷ 8 cores = 125 frames per core
- 10 seconds per frame = 1250 seconds total

**Distributed (10 machines, 80 cores):**

- 1000 frames ÷ 80 cores = 12.5 frames per core
- 10 seconds per frame = 125 seconds
- Network overhead: 1000 transfers × 50ms = 50 seconds
- **Total: 175 seconds (7x faster!)**

### Example 2: Simple API Calls (Local Wins)

**Task:** Make 100 API calls, each takes 50ms

**Local (1 machine, sequential):**

- 100 × 50ms = 5000ms

**Distributed (10 machines, 10 calls each):**

- 10 calls × 50ms = 500ms per machine
- Network coordination: 10 × 5ms = 50ms
- **Total: 550ms**

**But if local can parallelize:**

- 100 calls ÷ 8 cores = 12.5 calls per core
- 12.5 × 50ms = 625ms
- **Local parallelization is still faster!**

### Example 3: Web Search (Distributed Required)

**Task:** Search billions of web pages

**Why Distributed:**

- Single machine can't store all pages
- Single machine can't process all queries
- **Must be distributed by nature**

**Trade-off:** Communication overhead is acceptable because:

- Processing time is massive (seconds to minutes)
- Network overhead is tiny percentage
- No alternative (can't fit on one machine)

---

## Key Insights

### 1. **Distribution Adds Overhead**

Every distributed call pays:

- Serialization cost
- Network latency
- Deserialization cost
- Protocol overhead

### 2. **The Ratio Matters**

**Benefit = Computation Time / Communication Overhead**

- If ratio > 10: Distribution likely beneficial
- If ratio < 5: Distribution likely hurts performance
- If ratio 5-10: Depends on other factors

### 3. **Parallel != Distributed**

- **Parallel**: Same machine, shared memory, fast communication
- **Distributed**: Different machines, network, slower communication

**Best approach:** Use parallel on same machine, distribute only when necessary.

### 4. **Pipeline Dependencies Limit Benefits**

Your pipeline has **sequential dependencies**:

- A must finish before B
- B must finish before C
- C must finish before D

This limits how much you can benefit from distribution.

### 5. **Parallel Services Benefit More**

The parallel services (C1-C4) benefit from distribution if:

- They process for a long time
- They don't need frequent communication
- They can work independently

---

## Conclusion

### Why Your Distributed Setup Might Be Slower

1. **Short Processing Times**: 100-300ms is relatively short
2. **Network Overhead**: 5-10ms per call is significant relative to processing
3. **Sequential Dependencies**: Pipeline structure limits parallelism benefits
4. **Multiple Network Calls**: Each call adds overhead

### When Distribution Is Worth It

Distribution becomes beneficial when:

1. **Processing time >> Communication overhead** (10x or more)
2. **Need more resources** than one machine can provide
3. **Independent tasks** that don't require frequent communication
4. **Geographic requirements** (serving users in different locations)
5. **Fault tolerance** is critical

### For Your Assignment

Your distributed setup demonstrates:

- ✅ **Real-world trade-offs**: Network overhead vs computation
- ✅ **Performance measurement**: You can measure the actual overhead
- ✅ **Communication comparison**: RPC vs gRPC performance
- ✅ **Distributed patterns**: How services coordinate across network

**Even if it's slower, it's still valuable** because it shows:

- The cost of distribution
- When to use it and when not to
- How communication protocols affect performance
- Real-world microservices challenges

### Final Thought

**Distributed computing doesn't automatically make things faster. It trades computation for communication. The art is knowing when the trade-off is worth it.**

Your assignment showcases this perfectly: you'll demonstrate that local execution is faster, but you'll also show the overhead of different communication methods (RPC vs gRPC), which is valuable knowledge for real-world distributed systems design.

---

## Summary Table

| Aspect              | Parallel (Same Machine)             | Distributed (Network)        |
| ------------------- | ----------------------------------- | ---------------------------- |
| Communication Speed | ~0.001ms (memory)                   | ~1-10ms (network)            |
| Bandwidth           | 10-50 GB/s                          | 100-1000 MB/s                |
| Best For            | Short tasks, frequent communication | Long tasks, independent work |
| Overhead            | Minimal                             | Significant                  |
| Scaling             | Limited by cores                    | Limited by network           |
| Complexity          | Lower                               | Higher                       |
| Failure Handling    | Simple                              | Complex (network failures)   |

**Your Pipeline:**

- Local: Fastest (baseline)
- Distributed: Slower, but demonstrates real-world patterns and communication overhead
- **Value**: Understanding the trade-offs is more important than absolute speed!
