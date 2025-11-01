# Communication Setup Guide: RPC vs gRPC

This document describes how to set up RPC (RPyC) and gRPC communication layers for the pipeline services. This is a reference guide for implementing distributed communication in the future.

## Overview

### RPC (Remote Procedure Call) - RPyC

**RPyC** (Remote Python Call) is a Python library for transparent remote procedure calls. It allows Python objects to be accessed remotely as if they were local.

**Characteristics:**
- Simple to use and integrate
- Python-specific (works seamlessly with Python objects)
- Symmetric RPC (both client and server can call each other)
- Transparent object proxying
- Supports bidirectional communication
- Lower performance compared to binary protocols
- Security considerations needed (can expose vulnerabilities)

### gRPC (Google Remote Procedure Call)

**gRPC** is a high-performance, open-source RPC framework developed by Google. It uses HTTP/2 for transport and Protocol Buffers for serialization.

**Characteristics:**
- High performance with binary serialization
- Language-agnostic (supports multiple languages)
- Supports streaming (unary, server streaming, client streaming, bidirectional)
- Built-in support for load balancing, authentication, and more
- More complex setup (requires .proto definitions)
- Type-safe with Protocol Buffers
- Better for production microservices

## Service Port Assignments

Each service in the pipeline will run on a dedicated port:

| Service | Port | Description |
|---------|------|-------------|
| Service A (Story Generator) | 50051 | First service in pipeline |
| Service B (Story Analyzer) | 50052 | Second service in pipeline |
| Service C1 (Image Concept) | 50053 | Parallel service |
| Service C2 (Audio Script) | 50054 | Parallel service |
| Service C3 (Translation) | 50055 | Parallel service |
| Service C4 (Formatting) | 50056 | Parallel service |
| Service D (Aggregator) | 50057 | Final service in pipeline |

**Note:** For parallel services (C1-C4), they can all be invoked simultaneously from Service C (Parallel Hub).

## RPC (RPyC) Implementation Structure

### Service Wrapper Pattern

Each service function needs to be wrapped in an RPyC server:

```python
# Example: rpc/rpc_service_a.py
import rpyc
from rpyc.utils.server import ThreadedServer
from services.service_a_story_generator import process_service_a

class ServiceA(rpyc.Service):
    def exposed_process(self, message_dict):
        """Expose the service function via RPC."""
        # Convert dict back to PipelineMessage
        message = PipelineMessage.from_dict(message_dict)
        # Execute service
        result = process_service_a(message)
        # Convert back to dict for serialization
        return result.to_dict()

if __name__ == "__main__":
    server = ThreadedServer(ServiceA, port=50051)
    server.start()
```

### RPC Client Pattern

```python
# Example: rpc/rpc_client.py
import rpyc
from core.message import PipelineMessage

class RPCClient:
    def call_service_a(self, message: PipelineMessage) -> PipelineMessage:
        conn = rpyc.connect("localhost", 50051)
        result_dict = conn.root.process(message.to_dict())
        conn.close()
        return PipelineMessage.from_dict(result_dict)
```

### Message Serialization for RPyC

Since RPyC works with Python objects, we need to ensure `PipelineMessage` is serializable:

- Convert `PipelineMessage` to dict before sending
- Convert dict back to `PipelineMessage` after receiving
- Handle timestamp objects (convert to dict/numeric format)
- Ensure all nested structures are JSON-serializable

## gRPC Implementation Structure

### Protocol Buffer Definition

First, define the service interfaces in `.proto` file:

```protobuf
// pipeline.proto
syntax = "proto3";

package pipeline;

// Message format for pipeline communication
message PipelineMessage {
    string user_input = 1;
    optional string story_text = 2;
    map<string, string> analysis = 3;
    map<string, string> image_concept = 4;
    map<string, string> audio_script = 5;
    map<string, string> translations = 6;
    map<string, string> formatted_output = 7;
    map<string, TimestampRecord> timestamps = 8;
    map<string, string> metadata = 9;
}

message TimestampRecord {
    string service_name = 1;
    double received_time = 2;
    double start_time = 3;
    double end_time = 4;
}

// Service A definition
service StoryGeneratorService {
    rpc Process(PipelineMessage) returns (PipelineMessage);
}

// Service B definition
service StoryAnalyzerService {
    rpc Process(PipelineMessage) returns (PipelineMessage);
}

// Service C (Parallel Hub) definitions
service ImageConceptService {
    rpc Process(PipelineMessage) returns (PipelineMessage);
}

service AudioScriptService {
    rpc Process(PipelineMessage) returns (PipelineMessage);
}

service TranslationService {
    rpc Process(PipelineMessage) returns (PipelineMessage);
}

service FormattingService {
    rpc Process(PipelineMessage) returns (PipelineMessage);
}

// Service D definition
service AggregatorService {
    rpc Process(PipelineMessage) returns (PipelineMessage);
}
```

### Generate gRPC Code

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. pipeline.proto
```

This generates:
- `pipeline_pb2.py` - Protocol buffer message classes
- `pipeline_pb2_grpc.py` - gRPC service stubs

### gRPC Server Implementation

```python
# Example: grpc/grpc_server_a.py
import grpc
from concurrent import futures
import pipeline_pb2
import pipeline_pb2_grpc
from services.service_a_story_generator import process_service_a

class StoryGeneratorServiceImpl(pipeline_pb2_grpc.StoryGeneratorServiceServicer):
    def Process(self, request, context):
        # Convert protobuf message to PipelineMessage
        message = self._pb_to_message(request)
        # Execute service
        result = process_service_a(message)
        # Convert back to protobuf
        return self._message_to_pb(result)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pipeline_pb2_grpc.add_StoryGeneratorServiceServicer_to_server(
        StoryGeneratorServiceImpl(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
```

### gRPC Client Implementation

```python
# Example: grpc/grpc_client.py
import grpc
import pipeline_pb2
import pipeline_pb2_grpc

class gRPCClient:
    def call_service_a(self, message: PipelineMessage) -> PipelineMessage:
        channel = grpc.insecure_channel('localhost:50051')
        stub = pipeline_pb2_grpc.StoryGeneratorServiceStub(channel)
        pb_message = self._message_to_pb(message)
        response = stub.Process(pb_message)
        return self._pb_to_message(response)
```

## Pipeline Service Communication Flow

### Sequential Services (A → B → D)

```
Main Program
    ↓ (RPC/gRPC call)
Service A Server (port 50051)
    ↓ (RPC/gRPC call)
Service B Server (port 50052)
    ↓ (RPC/gRPC call)
Service C (Parallel Hub)
    ↓ (parallel RPC/gRPC calls)
Service D Server (port 50057)
    ↓ (return)
Main Program
```

### Parallel Services (C1, C2, C3, C4)

Service C (Parallel Hub) makes simultaneous calls:
- Service C1 (port 50053)
- Service C2 (port 50054)
- Service C3 (port 50055)
- Service C4 (port 50056)

Using concurrent futures or async/await to execute in parallel.

## Performance Comparison Points

When comparing RPC vs gRPC, measure:

1. **Latency per service call:**
   - Time from request sent to response received
   - Network overhead
   - Serialization/deserialization time

2. **Throughput:**
   - Requests per second
   - Bytes transferred
   - CPU/Memory usage

3. **Pipeline total time:**
   - End-to-end execution time
   - Compare local vs RPC vs gRPC
   - Account for network delays

4. **Resource utilization:**
   - CPU usage on server/client
   - Memory footprint
   - Network bandwidth

## Setup Instructions

### RPC (RPyC) Setup

1. Install RPyC:
   ```bash
   pip install rpyc
   ```

2. For each service, create a server script:
   - `rpc/rpc_server_a.py` (Service A)
   - `rpc/rpc_server_b.py` (Service B)
   - etc.

3. Start all service servers before running main program

4. Modify `main.py` to use RPC clients instead of local function calls

### gRPC Setup

1. Install gRPC tools:
   ```bash
   pip install grpcio grpcio-tools
   ```

2. Create `grpc/pipeline.proto` with service definitions

3. Generate Python code:
   ```bash
   python -m grpc_tools.protoc -I grpc --python_out=grpc --grpc_python_out=grpc grpc/pipeline.proto
   ```

4. Create server implementations for each service

5. Start all gRPC servers before running main program

6. Modify `main.py` to use gRPC clients instead of local function calls

## Notes

- Both RPC and gRPC implementations should maintain the same service interface
- Timestamps must be properly serialized/deserialized
- Error handling should be consistent across both methods
- The local mode (current implementation) serves as the baseline for performance comparison

