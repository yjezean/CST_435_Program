# Network Architecture Diagram

## Overview
This document provides visual representations of the distributed deployment architecture.

---

## Physical Deployment (2 Machines)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         NETWORK / INTERNET                              │
│                       (192.168.1.0/24 or similar)                       │
└────────────────────────┬──────────────────────────┬─────────────────────┘
                         │                          │
         ┌───────────────▼────────────┐  ┌──────────▼─────────────────┐
         │   MACHINE 1 (Controller)   │  │   MACHINE 2 (Worker)       │
         │   IP: 192.168.1.10        │  │   IP: 192.168.1.20         │
         └────────────────────────────┘  └────────────────────────────┘
```

---

## Machine 1 (Controller) - Detailed View

```
┌──────────────────────────────────────────────────────────────┐
│                    MACHINE 1 - 192.168.1.10                  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Docker Container: service-main                        │  │
│  │  Network: host                                         │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │  Main Program (Orchestrator)                 │    │  │
│  │  │  - Coordinates pipeline                      │    │  │
│  │  │  - Connects to local services (A, B)         │    │  │
│  │  │  - Connects to remote services (C, D)        │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Docker Container: story-generator-machine1            │  │
│  │  Network: host                                         │  │
│  │  Port: 50051 (gRPC) / 8051 (RPC)                      │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │  Service A: Story Generator                  │    │  │
│  │  │  - Generates stories from prompts            │    │  │
│  │  │  - First stage in pipeline                   │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Docker Container: story-analyzer-machine1             │  │
│  │  Network: host                                         │  │
│  │  Port: 50052 (gRPC) / 8052 (RPC)                      │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │  Service B: Story Analyzer                   │    │  │
│  │  │  - Analyzes sentiment and keywords           │    │  │
│  │  │  - Second stage in pipeline                  │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  Network Interface: 192.168.1.10                             │
│  Exposed Ports: 50051, 50052, 8051, 8052                     │
└──────────────────────────────────────────────────────────────┘
```

---

## Machine 2 (Worker) - Detailed View

```
┌────────────────────────────────────────────────────────────────────┐
│                    MACHINE 2 - 192.168.1.20                        │
│                                                                     │
│  Docker Network: pipeline-net-machine2 (bridge)                    │
│                                                                     │
│  ┌───────────────────────────┐  ┌───────────────────────────┐    │
│  │  Container: service-c1    │  │  Container: service-c2    │    │
│  │  Port: 50053              │  │  Port: 50054              │    │
│  │  ┌─────────────────────┐  │  │  ┌─────────────────────┐  │    │
│  │  │ Service C1:         │  │  │  │ Service C2:         │  │    │
│  │  │ Image Concept       │  │  │  │ Audio Script        │  │    │
│  │  └─────────────────────┘  │  │  └─────────────────────┘  │    │
│  └───────────────────────────┘  └───────────────────────────┘    │
│                                                                     │
│  ┌───────────────────────────┐  ┌───────────────────────────┐    │
│  │  Container: service-c3    │  │  Container: service-c4    │    │
│  │  Port: 50055              │  │  Port: 50056              │    │
│  │  ┌─────────────────────┐  │  │  ┌─────────────────────┐  │    │
│  │  │ Service C3:         │  │  │  │ Service C4:         │  │    │
│  │  │ Translation         │  │  │  │ Formatting          │  │    │
│  │  └─────────────────────┘  │  │  └─────────────────────┘  │    │
│  └───────────────────────────┘  └───────────────────────────┘    │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │  Container: parallel-hub-machine2                        │     │
│  │  Port: 50057 (exposed) + internal network               │     │
│  │  ┌────────────────────────────────────────────────────┐  │     │
│  │  │ Service C: Parallel Hub                            │  │     │
│  │  │ - Coordinates C1, C2, C3, C4                       │  │     │
│  │  │ - Runs parallel processing                         │  │     │
│  │  │ - Aggregates parallel results                      │  │     │
│  │  └────────────────────────────────────────────────────┘  │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │  Container: aggregator-machine2                          │     │
│  │  Port: 50058                                             │     │
│  │  ┌────────────────────────────────────────────────────┐  │     │
│  │  │ Service D: Final Aggregator                        │  │     │
│  │  │ - Combines all results                             │  │     │
│  │  │ - Validates completeness                           │  │     │
│  │  │ - Returns final package                            │  │     │
│  │  └────────────────────────────────────────────────────┘  │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│  Network Interface: 192.168.1.20                                   │
│  Exposed Ports: 50053-50058, 8053-8058                             │
└────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram (gRPC/RPC)

```
USER INPUT
    │
    ▼
┌─────────────────────────────────────────────────┐
│             MACHINE 1                           │
│  ┌───────────────────────────────────────────┐  │
│  │  Main Program                             │  │
│  │  - Receives user prompt                   │  │
│  └─────────────────┬─────────────────────────┘  │
│                    │                             │
│                    ▼                             │
│  ┌───────────────────────────────────────────┐  │
│  │  Service A: Story Generator               │  │
│  │  Input: user_input                        │  │
│  │  Output: story_text                       │  │
│  └─────────────────┬─────────────────────────┘  │
│                    │                             │
│                    ▼                             │
│  ┌───────────────────────────────────────────┐  │
│  │  Service B: Story Analyzer                │  │
│  │  Input: story_text                        │  │
│  │  Output: analysis                         │  │
│  └─────────────────┬─────────────────────────┘  │
│                    │                             │
└────────────────────┼─────────────────────────────┘
                     │
                     │ Network: gRPC/RPC
                     │ (192.168.1.10 → 192.168.1.20)
                     │
┌────────────────────▼─────────────────────────────┐
│             MACHINE 2                            │
│  ┌───────────────────────────────────────────┐  │
│  │  Service C: Parallel Hub                  │  │
│  │  Input: story_text, analysis              │  │
│  └─────┬────────────────────────────┬────────┘  │
│        │                            │            │
│        │ (Parallel Execution)       │            │
│        │                            │            │
│    ┌───▼────┐ ┌────▼────┐ ┌────▼───┐ ┌───▼───┐ │
│    │Service │ │Service  │ │Service │ │Service│ │
│    │  C1    │ │  C2     │ │  C3    │ │  C4   │ │
│    │ Image  │ │ Audio   │ │ Trans  │ │Format │ │
│    └───┬────┘ └────┬────┘ └────┬───┘ └───┬───┘ │
│        │           │            │          │     │
│        └───────────┴────────────┴──────────┘     │
│                    │                             │
│                    ▼                             │
│  ┌───────────────────────────────────────────┐  │
│  │  Service C: Parallel Hub                  │  │
│  │  Output: Combined parallel results        │  │
│  └─────────────────┬─────────────────────────┘  │
│                    │                             │
│                    ▼                             │
│  ┌───────────────────────────────────────────┐  │
│  │  Service D: Final Aggregator              │  │
│  │  Input: All results                       │  │
│  │  Output: Complete package                 │  │
│  └─────────────────┬─────────────────────────┘  │
│                    │                             │
└────────────────────┼─────────────────────────────┘
                     │
                     │ Network: gRPC/RPC
                     │ (192.168.1.20 → 192.168.1.10)
                     │
┌────────────────────▼─────────────────────────────┐
│             MACHINE 1                            │
│  ┌───────────────────────────────────────────┐  │
│  │  Main Program                             │  │
│  │  - Receives final package                 │  │
│  │  - Displays results                       │  │
│  │  - Saves to JSON                          │  │
│  └───────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
    │
    ▼
OUTPUT FILE
(pipeline_output_local_docker_grpc.json)
```

---

## Communication Protocols

### gRPC Communication (Default)

```
Machine 1                           Machine 2
────────────                       ────────────

Main Program
    │
    │ gRPC call (Protocol Buffers)
    │ Target: 192.168.1.20:50057
    │
    └──────────────────────────────►  Service C Hub
                                         │
                                         │ (Internal gRPC)
                                         ├────► Service C1 (50053)
                                         ├────► Service C2 (50054)
                                         ├────► Service C3 (50055)
                                         └────► Service C4 (50056)
                                         │
    ◄────────────────────────────────────┘
    │ gRPC response
    │
    │ gRPC call
    │ Target: 192.168.1.20:50058
    │
    └──────────────────────────────►  Service D Aggregator
                                         │
    ◄────────────────────────────────────┘
    │ gRPC response (final result)
```

### RPC Communication (Alternative)

```
Machine 1                           Machine 2
────────────                       ────────────

Main Program
    │
    │ JSON-over-TCP
    │ Target: 192.168.1.20:8057
    │ {"id": "1", "method": "process", "params": {...}}
    │
    └──────────────────────────────►  Service C Hub
                                         │
    ◄────────────────────────────────────┘
    │ JSON response
    │ {"id": "1", "result": {...}}
```

---

## Port Mapping Table

| Service | Container Name | Machine | gRPC Port | RPC Port | Protocol |
|---------|---------------|---------|-----------|----------|----------|
| Main | main-machine1 | 1 | - | - | Client |
| Service A | story-generator-machine1 | 1 | 50051 | 8051 | Server |
| Service B | story-analyzer-machine1 | 1 | 50052 | 8052 | Server |
| Service C1 | image-concept-machine2 | 2 | 50053 | 8053 | Server |
| Service C2 | audio-script-machine2 | 2 | 50054 | 8054 | Server |
| Service C3 | translation-machine2 | 2 | 50055 | 8055 | Server |
| Service C4 | formatting-machine2 | 2 | 50056 | 8056 | Server |
| Service C | parallel-hub-machine2 | 2 | 50057 | 8057 | Server |
| Service D | aggregator-machine2 | 2 | 50058 | 8058 | Server |

---

## Network Security Considerations

```
┌──────────────────────────────────────────────────────────┐
│                      FIREWALL RULES                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Machine 1 (Ingress)                                     │
│  ├─ Allow: 50051-50052/tcp (gRPC services)              │
│  ├─ Allow: 8051-8052/tcp (RPC services)                 │
│  └─ Block: All other inbound                            │
│                                                          │
│  Machine 1 (Egress)                                      │
│  └─ Allow: 50053-50058/tcp to 192.168.1.20              │
│                                                          │
│  Machine 2 (Ingress)                                     │
│  ├─ Allow: 50053-50058/tcp (gRPC services)              │
│  ├─ Allow: 8053-8058/tcp (RPC services)                 │
│  └─ Block: All other inbound                            │
│                                                          │
│  Machine 2 (Egress)                                      │
│  └─ Allow: Outbound responses to established            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Scaling Possibilities (Future)

### 3-Machine Setup (Example)

```
Machine 1 (Controller)      Machine 2 (Pipeline)     Machine 3 (Parallel)
    Main Program         →      Service A         ←
    Service D            ←      Service B         →   Service C Hub
                                Service C          →   Service C1
                                                   →   Service C2
                                                   →   Service C3
                                                   →   Service C4
```

### Load Balanced Setup (Example)

```
                            Load Balancer
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
              Machine 1      Machine 2    Machine 3
              Service C1     Service C2   Service C3
              (Image)        (Audio)      (Translation)
```

---

## Troubleshooting Network Issues

### Check Connectivity
```bash
# From Machine 1
ping 192.168.1.20
nc -zv 192.168.1.20 50057

# From Machine 2
ping 192.168.1.10
nc -zv 192.168.1.10 50051
```

### Verify Port Listening
```bash
# On Machine 1
netstat -tuln | grep -E "50051|50052"

# On Machine 2
netstat -tuln | grep -E "5005[3-8]"
```

### Test Service Response
```bash
# From Machine 1 container
docker exec main-machine1 python -c "
import socket
s = socket.socket()
s.connect(('192.168.1.20', 50057))
s.close()
print('Connected successfully')
"
```

---

This network architecture provides:
- ✅ Clear separation of concerns
- ✅ Scalable design
- ✅ Fault isolation
- ✅ Performance optimization through parallelization
- ✅ Protocol flexibility (gRPC/RPC)
- ✅ Easy troubleshooting
