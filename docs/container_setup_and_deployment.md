# Container Setup and Multi-Machine Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [Container Setup Instructions](#container-setup-instructions)
3. [Service Distribution Strategy](#service-distribution-strategy)
4. [Single Machine Deployment (Windows)](#single-machine-deployment-windows)
5. [Multi-Machine Deployment (Windows + Linux)](#multi-machine-deployment-windows--linux)
6. [Network Configuration](#network-configuration)
7. [Testing and Verification](#testing-and-verification)

---

## Overview

This guide provides step-by-step instructions for:

- Setting up Docker containers for the pipeline services
- Deploying services on a single machine (Windows)
- Distributing services across two machines (Windows + Linux) for performance comparison

### Deployment Scenarios

1. **Scenario A: Single Machine - All Containers**

   - All services in containers on Windows machine
   - Local Docker network communication
   - Baseline for container overhead

2. **Scenario B: Two Machines - Distributed Services**
   - Services distributed across Windows and Linux machines
   - Network communication between machines
   - Real-world distributed system demonstration

---

## Container Setup Instructions

### Prerequisites

**On Windows Machine:**

- Docker Desktop installed and running
- Python 3.8+ (for building/testing)
- Git (if cloning repository)

**On Linux Machine:**

- Docker installed and running
- Python 3.8+ (for building/testing)
- Network connectivity to Windows machine
- Firewall configured to allow Docker communication

### Step 1: Create Dockerfile for Each Service

Create a `docker/` directory and add Dockerfiles:

#### Base Dockerfile Template

**`docker/Dockerfile.base`**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY core/ ./core/
COPY utils/ ./utils/
COPY services/ ./services/
```

**`docker/Dockerfile.service-a`**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary modules
COPY core/ ./core/
COPY utils/ ./utils/
COPY services/service_a_story_generator.py ./services/

# Expose port
EXPOSE 50051

# Run service (will be implemented for RPC/gRPC)
CMD ["python", "-m", "services.service_a_story_generator"]
```

Repeat for other services (service-b, service-c1, service-c2, service-c3, service-c4, service-d).

### Step 2: Create Docker Compose File

**`docker/docker-compose.yml`** (for single machine)

```yaml
version: "3.8"

services:
  service-a:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-a
    container_name: story-generator
    networks:
      - pipeline-net
    environment:
      - SERVICE_NAME=service_a
      - SERVICE_PORT=50051
      - NEXT_SERVICE_HOST=service-b
      - NEXT_SERVICE_PORT=50052
      - PIPELINE_MODE=rpc # or grpc
    ports:
      - "50051:50051"

  service-b:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-b
    container_name: story-analyzer
    networks:
      - pipeline-net
    depends_on:
      - service-a
    environment:
      - SERVICE_NAME=service_b
      - SERVICE_PORT=50052
      - NEXT_SERVICE_HOST=service-c
      - NEXT_SERVICE_PORT=50053
      - PIPELINE_MODE=rpc
    ports:
      - "50052:50052"

  service-c1:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-c1
    container_name: image-concept
    networks:
      - pipeline-net
    environment:
      - SERVICE_NAME=service_c1
      - SERVICE_PORT=50053
      - PIPELINE_MODE=rpc
    ports:
      - "50053:50053"

  service-c2:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-c2
    container_name: audio-script
    networks:
      - pipeline-net
    environment:
      - SERVICE_NAME=service_c2
      - SERVICE_PORT=50054
      - PIPELINE_MODE=rpc
    ports:
      - "50054:50054"

  service-c3:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-c3
    container_name: translation
    networks:
      - pipeline-net
    environment:
      - SERVICE_NAME=service_c3
      - SERVICE_PORT=50055
      - PIPELINE_MODE=rpc
    ports:
      - "50055:50055"

  service-c4:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-c4
    container_name: formatting
    networks:
      - pipeline-net
    environment:
      - SERVICE_NAME=service_c4
      - SERVICE_PORT=50056
      - PIPELINE_MODE=rpc
    ports:
      - "50056:50056"

  service-c:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-c
    container_name: parallel-hub
    networks:
      - pipeline-net
    depends_on:
      - service-c1
      - service-c2
      - service-c3
      - service-c4
    environment:
      - SERVICE_NAME=service_c
      - SERVICE_PORT=50057
      - NEXT_SERVICE_HOST=service-d
      - NEXT_SERVICE_PORT=50058
      - C1_HOST=service-c1
      - C2_HOST=service-c2
      - C3_HOST=service-c3
      - C4_HOST=service-c4
      - PIPELINE_MODE=rpc
    ports:
      - "50057:50057"

  service-d:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-d
    container_name: aggregator
    networks:
      - pipeline-net
    depends_on:
      - service-c
    environment:
      - SERVICE_NAME=service_d
      - SERVICE_PORT=50058
      - PIPELINE_MODE=rpc
    ports:
      - "50058:50058"

networks:
  pipeline-net:
    driver: bridge
```

### Step 3: Build and Start Containers

```bash
# Navigate to docker directory
cd docker

# Build all images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

---

## Service Distribution Strategy

### Distribution Plan Across 2 Machines

**Goal:** Create an interesting comparison by distributing services to showcase:

- Network latency between machines
- Different processing loads on each machine
- Real-world distributed system patterns

### Recommended Distribution

#### **Machine 1: Windows (Primary/Orchestrator)**

- **Main Program** - Entry point, orchestrates pipeline
- **Service A (Story Generator)** - First service in pipeline
- **Service B (Story Analyzer)** - Second service
- **Service C (Parallel Hub)** - Coordinates parallel services
- **Service D (Aggregator)** - Final service

**Why:**

- Main program stays local (no network delay for user interaction)
- Sequential pipeline stays together (A→B→D) on one machine
- Hub (Service C) coordinates remote parallel services

#### **Machine 2: Linux (Parallel Workers)**

- **Service C1 (Image Concept)** - Parallel worker
- **Service C2 (Audio Script)** - Parallel worker
- **Service C3 (Translation)** - Parallel worker (longest processing)
- **Service C4 (Formatting)** - Parallel worker

**Why:**

- All parallel services on one machine
- Can showcase load balancing
- Network communication happens for parallel batch (interesting comparison)
- Service C3 (translation) takes longest - good for demonstrating network impact

### Alternative Distribution (More Interesting)

#### **Machine 1: Windows**

- **Main Program**
- **Service A (Story Generator)**
- **Service C2 (Audio Script)** - One parallel service
- **Service C4 (Formatting)** - One parallel service

#### **Machine 2: Linux**

- **Service B (Story Analyzer)**
- **Service C (Parallel Hub)**
- **Service C1 (Image Concept)** - Parallel service
- **Service C3 (Translation)** - Parallel service (longest)
- **Service D (Aggregator)**

**Why This Is More Interesting:**

- Pipeline is split: A (Win) → B (Linux) → C (Linux) → D (Linux)
- Shows network latency in sequential pipeline
- Parallel services split across machines
- Hub coordinates both local and remote services
- More realistic distributed system scenario

### Network Flow Visualization

**Alternative Distribution Flow:**

```
Windows Machine:
  Main Program
    ↓ (local call)
  Service A
    ↓ (NETWORK - RPC/gRPC)

Linux Machine:
  Service B
    ↓ (local call)
  Service C (Hub)
    ├─→ (local call) Service C1
    ├─→ (NETWORK - RPC/gRPC) Service C2 (Windows)
    ├─→ (local call) Service C3
    └─→ (NETWORK - RPC/gRPC) Service C4 (Windows)
    ↓ (collect all, local call)
  Service D
    ↓ (NETWORK - RPC/gRPC response)

Windows Machine:
  Main Program receives result
```

This creates:

- **1 network call** in sequential pipeline (A→B)
- **2 network calls** for parallel services (C2, C4)
- **1 network response** (D→Main)
- Total: **4 network interactions**, showcasing both sequential and parallel network overhead

---

## Single Machine Deployment (Windows)

### Step-by-Step Instructions

1. **Navigate to project directory:**

   ```bash
   cd "D:\YEAR4\SEM1\CST435 PARALLEL AND CLOUD COMPUTING\Assignment_1\Programs"
   ```

2. **Ensure Docker Desktop is running**

3. **Build containers:**

   ```bash
   cd docker
   docker-compose build
   ```

4. **Start all services:**

   ```bash
   docker-compose up -d
   ```

5. **Verify containers are running:**

   ```bash
   docker ps
   ```

   Should show all 8 containers (service-a through service-d, plus service-c1-c4)

6. **Check logs:**

   ```bash
   docker-compose logs service-a
   docker-compose logs service-b
   ```

7. **Test connectivity:**

   ```bash
   # From host, test if services are accessible
   telnet localhost 50051
   ```

8. **Run main program:**
   ```bash
   # From host Windows machine
   python main.py "A space adventure about robots"
   ```

---

## Multi-Machine Deployment (Windows + Linux)

### Prerequisites

1. **Network Setup:**

   - Both machines on same network (LAN)
   - Know IP addresses:
     - Windows machine IP: `192.168.1.XXX` (example)
     - Linux machine IP: `192.168.1.XXX` (example)
   - Test connectivity: `ping` between machines

2. **Firewall Configuration:**

   - Windows: Allow Docker through firewall
   - Linux: Open ports 50051-50058 in firewall

3. **Shared Codebase:**
   - Copy entire project to Linux machine
   - Or use Git to clone on Linux machine
   - Ensure same code version on both machines

### Step 1: Configure Linux Machine

1. **Install Docker (if not installed):**

   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io docker-compose
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker $USER  # Log out and back in
   ```

2. **Copy project to Linux:**

   ```bash
   # Option 1: Use Git
   git clone <repository_url>
   cd Programs

   # Option 2: Copy via SCP from Windows
   # From Windows PowerShell:
   # scp -r "D:\YEAR4\..." user@linux-ip:/path/to/destination
   ```

3. **Find Linux machine IP:**
   ```bash
   ip addr show
   # or
   hostname -I
   ```
   Note the IP address (e.g., `192.168.1.105`)

### Step 2: Create Machine-Specific Docker Compose Files

#### **Windows Machine: `docker/docker-compose.windows.yml`**

```yaml
version: "3.8"

services:
  main:
    build:
      context: ..
      dockerfile: docker/Dockerfile.main
    container_name: pipeline-main
    networks:
      - pipeline-net
    environment:
      - PIPELINE_MODE=rpc
      - SERVICE_A_HOST=192.168.1.XXX # Windows IP
      - SERVICE_A_PORT=50051
    ports:
      - "8080:8080" # Main program access port

  service-a:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-a
    container_name: story-generator
    networks:
      - pipeline-net
    environment:
      - SERVICE_NAME=service_a
      - SERVICE_PORT=50051
      - NEXT_SERVICE_HOST=192.168.1.YYY # Linux IP
      - NEXT_SERVICE_PORT=50052
      - PIPELINE_MODE=rpc
    ports:
      - "50051:50051"

  service-c2:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-c2
    container_name: audio-script
    networks:
      - pipeline-net
    environment:
      - SERVICE_NAME=service_c2
      - SERVICE_PORT=50054
      - PIPELINE_MODE=rpc
    ports:
      - "50054:50054"

  service-c4:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-c4
    container_name: formatting
    networks:
      - pipeline-net
    environment:
      - SERVICE_NAME=service_c4
      - SERVICE_PORT=50056
      - PIPELINE_MODE=rpc
    ports:
      - "50056:50056"

networks:
  pipeline-net:
    driver: bridge
```

#### **Linux Machine: `docker/docker-compose.linux.yml`**

```yaml
version: "3.8"

services:
  service-b:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-b
    container_name: story-analyzer
    networks:
      - pipeline-net
    environment:
      - SERVICE_NAME=service_b
      - SERVICE_PORT=50052
      - NEXT_SERVICE_HOST=localhost # Service C on same machine
      - NEXT_SERVICE_PORT=50057
      - PIPELINE_MODE=rpc
    ports:
      - "50052:50052"

  service-c:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-c
    container_name: parallel-hub
    networks:
      - pipeline-net
    depends_on:
      - service-c1
      - service-c3
    environment:
      - SERVICE_NAME=service_c
      - SERVICE_PORT=50057
      - NEXT_SERVICE_HOST=localhost
      - NEXT_SERVICE_PORT=50058
      - C1_HOST=localhost
      - C1_PORT=50053
      - C2_HOST=192.168.1.XXX # Windows IP
      - C2_PORT=50054
      - C3_HOST=localhost
      - C3_PORT=50055
      - C4_HOST=192.168.1.XXX # Windows IP
      - C4_PORT=50056
      - PIPELINE_MODE=rpc
    ports:
      - "50057:50057"

  service-c1:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-c1
    container_name: image-concept
    networks:
      - pipeline-net
    environment:
      - SERVICE_NAME=service_c1
      - SERVICE_PORT=50053
      - PIPELINE_MODE=rpc
    ports:
      - "50053:50053"

  service-c3:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-c3
    container_name: translation
    networks:
      - pipeline-net
    environment:
      - SERVICE_NAME=service_c3
      - SERVICE_PORT=50055
      - PIPELINE_MODE=rpc
    ports:
      - "50055:50055"

  service-d:
    build:
      context: ..
      dockerfile: docker/Dockerfile.service-d
    container_name: aggregator
    networks:
      - pipeline-net
    depends_on:
      - service-c
    environment:
      - SERVICE_NAME=service_d
      - SERVICE_PORT=50058
      - PIPELINE_MODE=rpc
    ports:
      - "50058:50058"

networks:
  pipeline-net:
    driver: bridge
```

### Step 3: Update Service Code for Network Configuration

Services need to read environment variables to determine:

- Whether to call next service locally or remotely
- What host/port to connect to

Example modification needed in services:

```python
import os

# Get configuration from environment
next_service_host = os.getenv('NEXT_SERVICE_HOST', 'localhost')
next_service_port = int(os.getenv('NEXT_SERVICE_PORT', '50052'))
pipeline_mode = os.getenv('PIPELINE_MODE', 'local')

# Use RPC/gRPC client if remote, direct call if local
if pipeline_mode in ['rpc', 'grpc']:
    # Call remote service via network
    result = rpc_client.call_service(next_service_host, next_service_port, message)
else:
    # Direct function call
    result = service_function(message)
```

### Step 4: Deploy on Linux Machine

1. **SSH into Linux machine:**

   ```bash
   ssh user@linux-machine-ip
   ```

2. **Navigate to project:**

   ```bash
   cd Programs
   ```

3. **Build containers:**

   ```bash
   cd docker
   docker-compose -f docker-compose.linux.yml build
   ```

4. **Start services:**

   ```bash
   docker-compose -f docker-compose.linux.yml up -d
   ```

5. **Verify:**
   ```bash
   docker ps
   # Should show: service-b, service-c, service-c1, service-c3, service-d
   ```

### Step 5: Deploy on Windows Machine

1. **Open PowerShell or Command Prompt**

2. **Navigate to project:**

   ```bash
   cd "D:\YEAR4\SEM1\CST435 PARALLEL AND CLOUD COMPUTING\Assignment_1\Programs"
   ```

3. **Update IP addresses in docker-compose.windows.yml:**

   - Replace `192.168.1.XXX` with Linux machine IP

4. **Build containers:**

   ```bash
   cd docker
   docker-compose -f docker-compose.windows.yml build
   ```

5. **Start services:**

   ```bash
   docker-compose -f docker-compose.windows.yml up -d
   ```

6. **Verify:**
   ```powershell
   docker ps
   # Should show: main, service-a, service-c2, service-c4
   ```

### Step 6: Test Network Connectivity

**From Windows machine:**

```powershell
# Test connection to Linux services
Test-NetConnection -ComputerName <linux-ip> -Port 50052
Test-NetConnection -ComputerName <linux-ip> -Port 50053
```

**From Linux machine:**

```bash
# Test connection to Windows services
telnet <windows-ip> 50051
telnet <windows-ip> 50054
```

---

## Network Configuration

### Firewall Rules

#### Windows Firewall:

1. Open Windows Defender Firewall
2. Allow Docker Desktop through firewall
3. Create inbound rules for ports 50051-50058
   - PowerShell:
   ```powershell
   New-NetFirewallRule -DisplayName "Pipeline Service A" -Direction Inbound -LocalPort 50051 -Protocol TCP -Action Allow
   # Repeat for other ports
   ```

#### Linux Firewall (UFW):

```bash
sudo ufw allow 50052/tcp
sudo ufw allow 50053/tcp
sudo ufw allow 50055/tcp
sudo ufw allow 50057/tcp
sudo ufw allow 50058/tcp
sudo ufw reload
sudo ufw status
```

#### Linux Firewall (iptables):

```bash
sudo iptables -A INPUT -p tcp --dport 50052 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 50053 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 50055 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 50057 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 50058 -j ACCEPT
sudo iptables-save
```

### Network Discovery

**Find Windows IP:**

```powershell
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.104)
```

**Find Linux IP:**

```bash
ip addr show
# or
ifconfig
# Look for inet address (e.g., 192.168.1.105)
```

### Docker Network Configuration

For cross-machine communication, containers should use:

- **Host machine IP** (not container names)
- **Exposed ports** on host machines
- **Bridge network** for local services, **host network** for remote services

---

## Testing and Verification

### Test 1: Local Communication (Each Machine)

**Windows:**

```bash
# Test service-a can reach service-c2 locally
docker exec -it story-generator ping -c 2 service-c2
```

**Linux:**

```bash
# Test service-b can reach service-c locally
docker exec -it story-analyzer ping -c 2 service-c
```

### Test 2: Cross-Machine Communication

**From Windows container to Linux:**

```bash
docker exec -it story-generator ping -c 2 <linux-ip>
docker exec -it story-generator telnet <linux-ip> 50052
```

**From Linux container to Windows:**

```bash
docker exec -it story-analyzer ping -c 2 <windows-ip>
docker exec -it story-analyzer telnet <windows-ip> 50051
```

### Test 3: End-to-End Pipeline

1. **Start all services on both machines**

2. **Run main program on Windows:**

   ```bash
   python main.py "A space adventure about robots"
   ```

3. **Monitor logs on both machines:**

   **Windows:**

   ```bash
   docker-compose -f docker-compose.windows.yml logs -f
   ```

   **Linux:**

   ```bash
   docker-compose -f docker-compose.linux.yml logs -f
   ```

4. **Check timestamps in output:**
   - Network calls should show longer duration
   - Compare with local execution baseline

### Expected Performance Differences

| Scenario                  | Expected Time | Notes                      |
| ------------------------- | ------------- | -------------------------- |
| Local execution           | ~500ms        | Baseline                   |
| Single machine containers | ~520-615ms    | Container + RPC overhead   |
| Two machines (RPC)        | ~600-750ms    | Additional network latency |
| Two machines (gRPC)       | ~550-650ms    | Better than RPC            |

---

## Troubleshooting

### Issue: Cannot connect between machines

**Solutions:**

1. Check firewall rules on both machines
2. Verify IP addresses are correct
3. Ensure services are bound to `0.0.0.0`, not `127.0.0.1`
4. Test with `telnet` or `ping` first
5. Check Docker network configuration

### Issue: Services not starting

**Solutions:**

1. Check Docker logs: `docker logs <container-name>`
2. Verify all dependencies are in requirements.txt
3. Check environment variables are set correctly
4. Ensure ports are not already in use

### Issue: Slow performance

**Solutions:**

1. Check network latency: `ping` between machines
2. Verify containers have sufficient resources
3. Check system load on both machines
4. Ensure Docker Desktop has enough memory allocated (Windows)

---

## Next Steps

After setting up containers:

1. **Implement RPC layer** - See `docs/communication_setup.md`
2. **Implement gRPC layer** - See `docs/communication_setup.md`
3. **Run performance comparisons** - Compare all three modes
4. **Collect metrics** - Measure and document differences
5. **Create report** - Document findings and analysis

---

## Summary

This setup allows you to:

- ✅ Run services in containers (single machine)
- ✅ Distribute services across two machines
- ✅ Compare local, RPC, and gRPC performance
- ✅ Measure network overhead in distributed systems
- ✅ Demonstrate real-world microservices architecture

The distributed setup showcases:

- Network latency in sequential pipeline
- Parallel service coordination across network
- Realistic distributed system patterns
- Clear performance differences between communication methods
