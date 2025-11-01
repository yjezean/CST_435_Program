# Performance Comparison: Local vs RPC vs gRPC in Containers

## Overview

This document explains what happens when services are separated into containers and communicate via RPC (RPyC) or gRPC, and which method is expected to be faster.

## Current Local Execution (Baseline)

### What Happens:
- **Direct function calls** - Services execute as regular Python function calls
- **Same memory space** - All services share the same process memory
- **No network overhead** - Zero network latency or serialization cost
- **Fastest possible** - This is the theoretical lower bound for execution time

### Performance Characteristics:
- Processing time = Pure computation time only
- Timestamps reflect actual service work
- Total pipeline time = Sum of sequential services + Max of parallel services

## Containerized Architecture

### What Changes:

When services are containerized, each service runs in:
- **Separate process** - Each container is an isolated process
- **Separate network namespace** - Containers communicate via network
- **Network isolation** - Even on same machine, Docker uses network bridges
- **Resource isolation** - Each container has its own CPU/memory allocation

### Impact:
1. **Container startup overhead** - Each container needs initialization time
2. **Network communication** - Even localhost requires network stack
3. **Inter-process communication** - Data must be serialized and transmitted
4. **Container networking overhead** - Docker bridge network adds latency

## RPC (RPyC) Communication

### How It Works:

**RPyC (Remote Python Call)** is a Python-specific RPC framework:

1. **Client Side:**
   - Converts Python objects to serialized format
   - Sends data over TCP socket
   - Waits for response

2. **Network Layer:**
   - TCP connection established
   - Data transmitted as serialized Python objects (pickle by default)
   - Connection maintained (stateful)

3. **Server Side:**
   - Receives serialized data
   - Deserializes to Python objects
   - Executes service function
   - Serializes result
   - Sends back response

### Performance Characteristics:

**Advantages:**
- **Python-native** - Seamless object proxying, works with complex Python types
- **Simple to use** - Minimal code changes required
- **Transparent** - Remote objects appear as local objects

**Disadvantages:**
- **Pickle serialization** - Slow for large/complex objects
- **Text-based protocol** - Not optimized for speed
- **Overhead** - Python object serialization is CPU-intensive
- **Security concerns** - Pickle can execute arbitrary code
- **TCP overhead** - Connection establishment and teardown costs

### Expected Performance Impact:

For your pipeline:

```
Service A → Service B (via RPC):
  - Serialization: ~5-10ms (story text + metadata)
  - Network transmission: ~1-2ms (local Docker network)
  - Deserialization: ~5-10ms
  - Total overhead: ~11-22ms per call

Parallel Services (C1-C4 via RPC):
  - Each has same overhead
  - But they run in parallel, so total overhead = max of individual overheads
  - Expected: ~15-25ms additional per parallel service
```

**Total Expected Overhead:**
- Sequential calls (A→B→C→D): ~44-88ms
- Parallel calls (C1, C2, C3, C4): ~15-25ms (max)
- **Total RPC overhead: ~60-115ms**

## gRPC Communication

### How It Works:

**gRPC** uses Protocol Buffers and HTTP/2:

1. **Client Side:**
   - Converts Python objects to Protocol Buffer format
   - Sends over HTTP/2 connection
   - Waits for response

2. **Network Layer:**
   - HTTP/2 multiplexed connection
   - Binary Protocol Buffer encoding
   - Connection pooling/reuse

3. **Server Side:**
   - Receives Protocol Buffer binary data
   - Deserializes using generated code (fast)
   - Executes service function
   - Serializes result to Protocol Buffer
   - Sends binary response

### Performance Characteristics:

**Advantages:**
- **Binary protocol** - Much faster serialization than pickle
- **HTTP/2 multiplexing** - Multiple requests over single connection
- **Efficient encoding** - Protocol Buffers are compact and fast
- **Streaming support** - Can handle large data efficiently
- **Language agnostic** - Works across different languages efficiently
- **Connection reuse** - Lower connection overhead

**Disadvantages:**
- **More complex setup** - Requires .proto definitions and code generation
- **Less Pythonic** - More explicit conversion needed
- **Learning curve** - More setup complexity

### Expected Performance Impact:

For your pipeline:

```
Service A → Service B (via gRPC):
  - Protocol Buffer encoding: ~1-3ms (much faster than pickle)
  - Network transmission: ~1-2ms (same as RPC, but HTTP/2 more efficient)
  - Protocol Buffer decoding: ~1-3ms
  - Total overhead: ~3-8ms per call

Parallel Services (C1-C4 via gRPC):
  - HTTP/2 multiplexing allows efficient parallel calls
  - Each call: ~3-8ms overhead
  - But multiplexing reduces overhead
  - Expected: ~5-10ms additional per parallel service
```

**Total Expected Overhead:**
- Sequential calls (A→B→C→D): ~12-32ms
- Parallel calls (C1, C2, C3, C4): ~5-10ms (with multiplexing)
- **Total gRPC overhead: ~20-45ms**

## Performance Comparison Summary

### Expected Execution Times (Example):

Assuming local execution takes **~500ms** (based on your current processing):

| Execution Mode | Expected Time | Overhead | Notes |
|---------------|---------------|----------|-------|
| **Local (Baseline)** | ~500ms | 0ms | Direct function calls |
| **RPC in Containers** | ~560-615ms | 60-115ms | ~12-23% slower |
| **gRPC in Containers** | ~520-545ms | 20-45ms | ~4-9% slower |

### Why gRPC is Faster:

1. **Binary Protocol vs Text Protocol**
   - gRPC uses compact binary Protocol Buffers
   - RPC uses larger pickle serialization (text-like binary)
   - Binary is ~3-5x faster to serialize/deserialize

2. **HTTP/2 Multiplexing**
   - Multiple requests can share single connection
   - Reduces connection overhead
   - Better for parallel services

3. **Optimized Serialization**
   - Protocol Buffer code is generated and optimized
   - Pickle is interpreted Python code (slower)

4. **Connection Efficiency**
   - HTTP/2 connection reuse
   - Less TCP overhead per request

## Real-World Considerations

### Factors That Affect Performance:

1. **Data Size:**
   - Larger messages (like your story text) → bigger difference
   - gRPC advantage grows with message size
   - Small messages: both are fast, difference is minimal

2. **Network Latency:**
   - Same machine (Docker): Latency ~0.1-1ms
   - Different machines: Latency ~1-10ms (depends on network)
   - Network latency affects both equally, but gRPC's multiplexing helps

3. **Parallel Service Efficiency:**
   - RPC: Each parallel call = separate TCP connection
   - gRPC: Parallel calls share HTTP/2 connection (more efficient)

4. **Container Overhead:**
   - Container startup: ~100-500ms (one-time per container)
   - Container runtime: Minimal (but measurable)
   - Both RPC and gRPC have same container overhead

5. **CPU Usage:**
   - RPC pickle serialization: More CPU-intensive
   - gRPC Protocol Buffer: Less CPU-intensive
   - Higher CPU usage can slow other operations

## Expected Results for Your Pipeline

### Scenario 1: Same Machine, Docker Containers

**Local Execution:**
- Total: ~500ms (example)
- Breakdown: Processing time only

**RPC Execution:**
- Total: ~560-615ms
- Breakdown:
  - Processing: ~500ms
  - RPC overhead: ~60-115ms
  - Container overhead: ~0ms (containers already running)

**gRPC Execution:**
- Total: ~520-545ms
- Breakdown:
  - Processing: ~500ms
  - gRPC overhead: ~20-45ms
  - Container overhead: ~0ms

**Winner: gRPC is ~40-70ms faster (~7-13% improvement)**

### Scenario 2: Different Machines (Network)

**RPC Execution:**
- Total: ~600-700ms (network latency adds ~40-85ms)
- Network latency affects each call

**gRPC Execution:**
- Total: ~550-600ms (network latency adds ~30-55ms)
- HTTP/2 multiplexing reduces repeated connection costs

**Winner: gRPC advantage increases with network distance**

## Practical Recommendations

### Use gRPC When:
- ✅ Performance is critical
- ✅ Services communicate frequently
- ✅ You have parallel service calls (like your C1-C4)
- ✅ Data payloads are medium to large
- ✅ You want production-ready solution

### Use RPC (RPyC) When:
- ✅ Rapid prototyping
- ✅ Simple setup needed
- ✅ Working with complex Python objects
- ✅ Performance is not the primary concern
- ✅ Small team or educational project

### For Your Assignment:

**Best Choice: gRPC**
- Shows clear performance advantage
- Demonstrates modern microservices architecture
- Better showcases the overhead of distributed systems
- More realistic for production scenarios
- Better comparison against baseline

## Measurement Strategy

When you measure, you'll see:

1. **Local (Baseline):**
   - Fastest execution
   - No network overhead visible
   - Pure computation time

2. **RPC:**
   - Noticeable overhead in timestamps
   - Each service call shows extra time
   - Parallel services show individual overhead

3. **gRPC:**
   - Lower overhead than RPC
   - More consistent timing
   - Better parallel service efficiency

## Conclusion

**gRPC will be faster** than RPC in containerized environments because:
1. Binary Protocol Buffers are faster than pickle
2. HTTP/2 multiplexing is more efficient
3. Less CPU overhead
4. Better connection reuse

**Expected Performance Order:**
1. **Local** (fastest) - baseline
2. **gRPC in Containers** (~4-9% slower than local)
3. **RPC in Containers** (~12-23% slower than local)

The actual numbers will depend on:
- Your story length (data size)
- Network conditions
- Container resource allocation
- System load

But the **relative performance relationship** (gRPC faster than RPC) will hold true in most scenarios.

