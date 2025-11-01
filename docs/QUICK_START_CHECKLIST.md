# Quick Start Checklist - Container Deployment

## Single Machine Setup (Windows)

### Prerequisites

- [ ] Docker Desktop installed and running
- [ ] Python 3.8+ installed
- [ ] Project code in local directory

### Steps

1. [ ] Navigate to project: `cd Programs`
2. [ ] Create docker directory structure (if not exists)
3. [ ] Create Dockerfiles for each service
4. [ ] Create `docker-compose.yml` file
5. [ ] Build images: `docker-compose build`
6. [ ] Start services: `docker-compose up -d`
7. [ ] Verify containers: `docker ps`
8. [ ] Test: Run `python main.py` from host

---

## Two Machine Setup (Windows + Linux)

### Prerequisites

**Windows Machine:**

- [ ] Docker Desktop installed
- [ ] Firewall configured (ports 50051, 50054, 50056)
- [ ] Know Windows IP address

**Linux Machine:**

- [ ] Docker installed (`sudo apt install docker.io`)
- [ ] Docker Compose installed
- [ ] Firewall configured (ports 50052, 50053, 50055, 50057, 50058)
- [ ] Know Linux IP address
- [ ] Project code copied/cloned to Linux

### Distribution Plan

**Windows Machine Runs:**

- [ ] Main Program
- [ ] Service A (Story Generator)
- [ ] Service C2 (Audio Script) - Parallel
- [ ] Service C4 (Formatting) - Parallel

**Linux Machine Runs:**

- [ ] Service B (Story Analyzer)
- [ ] Service C (Parallel Hub)
- [ ] Service C1 (Image Concept) - Parallel
- [ ] Service C3 (Translation) - Parallel
- [ ] Service D (Aggregator)

### Network Flow

```
Windows: Main → A → (NETWORK) →
Linux: B → C → [C1, C3 (local), C2, C4 (network)] → D → (NETWORK) →
Windows: Main receives result
```

### Steps

#### On Linux Machine:

1. [ ] Find IP: `ip addr show` or `hostname -I`
2. [ ] Configure firewall: `sudo ufw allow 50052-50058/tcp`
3. [ ] Navigate to project: `cd Programs`
4. [ ] Create `docker-compose.linux.yml`
5. [ ] Update IPs in compose file (Windows IP)
6. [ ] Build: `docker-compose -f docker-compose.linux.yml build`
7. [ ] Start: `docker-compose -f docker-compose.linux.yml up -d`
8. [ ] Verify: `docker ps` (should show 5 containers)

#### On Windows Machine:

1. [ ] Find IP: `ipconfig` (look for IPv4)
2. [ ] Configure Windows Firewall (ports 50051, 50054, 50056)
3. [ ] Navigate to project
4. [ ] Create `docker-compose.windows.yml`
5. [ ] Update IPs in compose file (Linux IP)
6. [ ] Build: `docker-compose -f docker-compose.windows.yml build`
7. [ ] Start: `docker-compose -f docker-compose.windows.yml up -d`
8. [ ] Verify: `docker ps` (should show 4 containers)

#### Testing:

1. [ ] Test connectivity: `ping` between machines
2. [ ] Test ports: `telnet <linux-ip> 50052`
3. [ ] Check logs: `docker-compose logs -f`
4. [ ] Run pipeline: `python main.py "test prompt"`

---

## Service Port Assignments

| Service    | Port  | Machine | Notes              |
| ---------- | ----- | ------- | ------------------ |
| Service A  | 50051 | Windows | First in pipeline  |
| Service B  | 50052 | Linux   | Second in pipeline |
| Service C1 | 50053 | Linux   | Parallel service   |
| Service C2 | 50054 | Windows | Parallel service   |
| Service C3 | 50055 | Linux   | Parallel service   |
| Service C4 | 50056 | Windows | Parallel service   |
| Service C  | 50057 | Linux   | Parallel hub       |
| Service D  | 50058 | Linux   | Final aggregator   |

---

## Environment Variables Needed

Each service needs:

- `SERVICE_NAME` - Name of service
- `SERVICE_PORT` - Port number
- `NEXT_SERVICE_HOST` - IP or hostname of next service
- `NEXT_SERVICE_PORT` - Port of next service
- `PIPELINE_MODE` - `local`, `rpc`, or `grpc`
- `C1_HOST`, `C2_HOST`, etc. - For parallel services (Service C only)

---

## Common Issues

### Cannot connect between machines

- [ ] Check firewalls on both machines
- [ ] Verify IP addresses are correct
- [ ] Ensure services bind to `0.0.0.0`, not `127.0.0.1`
- [ ] Test with `ping` and `telnet` first

### Services not starting

- [ ] Check logs: `docker logs <container-name>`
- [ ] Verify all code is copied to Linux
- [ ] Check environment variables are set
- [ ] Ensure ports are not in use

### Slow performance

- [ ] Check network latency: `ping`
- [ ] Verify Docker has enough resources
- [ ] Check system load on both machines

---

## Performance Comparison Order

1. **Baseline**: Local execution (no containers)
2. **Container Baseline**: Single machine, all containers
3. **RPC Single Machine**: Containers with RPC
4. **gRPC Single Machine**: Containers with gRPC
5. **RPC Two Machines**: Distributed with RPC
6. **gRPC Two Machines**: Distributed with gRPC

**Expected Speed Order:**
Local > gRPC Single > RPC Single > gRPC Two > RPC Two

---

## Quick Commands Reference

```bash
# Docker
docker ps                    # List running containers
docker logs <name>           # View logs
docker exec -it <name> sh    # Enter container

# Docker Compose
docker-compose up -d         # Start services
docker-compose down          # Stop services
docker-compose logs -f       # Follow logs
docker-compose build         # Build images

# Network Testing
ping <ip>                    # Test connectivity
telnet <ip> <port>          # Test port
netstat -an | grep <port>   # Check if port open
```

---

## Next Steps After Setup

1. [ ] Implement RPC communication layer
2. [ ] Implement gRPC communication layer
3. [ ] Run performance tests for each mode
4. [ ] Collect timestamp data
5. [ ] Compare results and document findings
6. [ ] Create performance report

---

## Key Files to Create

- [ ] `docker/Dockerfile.service-a`
- [ ] `docker/Dockerfile.service-b`
- [ ] `docker/Dockerfile.service-c`
- [ ] `docker/Dockerfile.service-c1` through `service-c4`
- [ ] `docker/Dockerfile.service-d`
- [ ] `docker/docker-compose.yml` (single machine)
- [ ] `docker/docker-compose.windows.yml` (Windows)
- [ ] `docker/docker-compose.linux.yml` (Linux)

See `docs/container_setup_and_deployment.md` for detailed instructions.
