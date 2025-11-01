# Docker Deployment Guide

This document describes the Docker containerization strategy for deploying the pipeline services. This is a reference guide for setting up containerized deployments.

## Container Architecture

### Strategy: One Container Per Service

Each service will run in its own Docker container for:
- **Isolation**: Each service operates independently
- **Scalability**: Services can be scaled individually
- **Resource management**: Assign resources per service
- **Debugging**: Easier to identify issues per service

### Service Container Mapping

| Service | Container Name | Image Tag |
|---------|----------------|-----------|
| Service A | `story-generator` | `pipeline/service-a:latest` |
| Service B | `story-analyzer` | `pipeline/service-b:latest` |
| Service C1 | `image-concept` | `pipeline/service-c1:latest` |
| Service C2 | `audio-script` | `pipeline/service-c2:latest` |
| Service C3 | `translation` | `pipeline/service-c3:latest` |
| Service C4 | `formatting` | `pipeline/service-c4:latest` |
| Service D | `aggregator` | `pipeline/service-d:latest` |
| Main Program | `pipeline-main` | `pipeline/main:latest` |

## Docker Network Configuration

### Network Setup

Create a Docker network for inter-container communication:

```bash
docker network create pipeline-network
```

Or in docker-compose, define a custom network:

```yaml
networks:
  pipeline-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Container Communication

- **Same Machine (Local Docker):**
  - Containers communicate via Docker network using service names as hostnames
  - Example: `service-a:50051` instead of `localhost:50051`

- **Multiple Machines:**
  - Use host IP addresses or Docker Swarm overlay network
  - Configure network discovery and service discovery

## Port Mapping Strategy

### Development/Local Docker

Map container ports to host ports for easy access:

```yaml
ports:
  - "50051:50051"  # Service A
  - "50052:50052"  # Service B
  # etc.
```

### Production

Use Docker networks only (no host port mapping) for security:
- Containers communicate internally
- Only expose main program or API gateway port

## Volume Mounts

### Shared Data Volumes

1. **Output Directory:**
   ```yaml
   volumes:
     - ./output:/app/output
   ```

2. **Logs Directory:**
   ```yaml
   volumes:
     - ./logs:/app/logs
   ```

3. **Configuration (optional):**
   ```yaml
   volumes:
     - ./config:/app/config:ro  # Read-only
   ```

### Code Mounting (Development)

For development, mount source code:

```yaml
volumes:
  - .:/app
  - /app/__pycache__  # Exclude cache
```

## Environment Variables

Each container should support these environment variables:

```yaml
environment:
  - SERVICE_NAME=service_a
  - SERVICE_PORT=50051
  - LOG_LEVEL=INFO
  - NEXT_SERVICE_HOST=service_b  # For pipeline flow
  - NEXT_SERVICE_PORT=50052
  - PIPELINE_MODE=local|rpc|grpc
```

## Docker Compose Structure Overview

### docker-compose.yml Structure

```yaml
version: '3.8'

services:
  service-a:
    build:
      context: .
      dockerfile: docker/Dockerfile.service-a
    container_name: story-generator
    networks:
      - pipeline-net
    environment:
      - SERVICE_NAME=service_a
      - SERVICE_PORT=50051
      - NEXT_SERVICE_HOST=service-b
      - NEXT_SERVICE_PORT=50052
    # ports mapping only for local development
    
  service-b:
    build:
      context: .
      dockerfile: docker/Dockerfile.service-b
    container_name: story-analyzer
    networks:
      - pipeline-net
    depends_on:
      - service-a
    # ... similar config
    
  service-c1:
    # Parallel service
    # ... config
    
  service-c2:
    # Parallel service
    # ... config
    
  service-c3:
    # Parallel service
    # ... config
    
  service-c4:
    # Parallel service
    # ... config
    
  service-d:
    # Final aggregator
    # ... config
    
  main:
    build:
      context: .
      dockerfile: docker/Dockerfile.main
    container_name: pipeline-main
    networks:
      - pipeline-net
    depends_on:
      - service-a
      - service-b
      - service-c1
      - service-c2
      - service-c3
      - service-c4
      - service-d
    volumes:
      - ./output:/app/output

networks:
  pipeline-net:
    driver: bridge
```

## Deployment Scenarios

### Scenario 1: Single Machine - All Containers

**Configuration:**
- All services in containers on one machine
- Docker network for inter-container communication
- Port mapping for external access (if needed)

**Setup Steps:**
1. Build all Docker images
2. Create Docker network
3. Start all containers using docker-compose
4. Run main program (in container or host)

**Command:**
```bash
docker-compose up -d
```

### Scenario 2: Single Machine - Mixed (Main on Host, Services in Containers)

**Configuration:**
- Main program runs on host machine
- All services run in Docker containers
- Host connects to containers via `localhost:PORT`

**Setup Steps:**
1. Build service images
2. Start service containers with port mapping
3. Run main program on host using containerized service ports

**Command:**
```bash
# Start services only
docker-compose up service-a service-b service-c1 service-c2 service-c3 service-c4 service-d

# Run main on host
python main.py
```

### Scenario 3: Multiple Machines - Distributed Containers

**Configuration:**
- Services distributed across multiple machines
- Each machine runs one or more service containers
- Communication via network IPs

**Setup Steps:**
1. Install Docker on each machine
2. Build images on each machine (or use registry)
3. Configure network connectivity
4. Set service discovery (hostnames/IPs)
5. Update service connection strings

**Example:**
- Machine 1 (192.168.1.10): Service A, Service B
- Machine 2 (192.168.1.11): Service C1, Service C2, Service C3, Service C4
- Machine 3 (192.168.1.12): Service D, Main Program

**Configuration:**
```yaml
# On Machine 1
environment:
  - NEXT_SERVICE_HOST=192.168.1.11  # Service C on Machine 2

# On Machine 2
environment:
  - NEXT_SERVICE_HOST=192.168.1.12  # Service D on Machine 3
```

### Scenario 4: Docker Swarm (Advanced)

For production orchestration:
- Use Docker Swarm or Kubernetes
- Service discovery built-in
- Load balancing and scaling
- Health checks and auto-restart

## Container Setup Instructions

### Basic Dockerfile Template

Each service needs its own Dockerfile (template):

```dockerfile
# docker/Dockerfile.service-a
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/ ./services/
COPY core/ ./core/
COPY utils/ ./utils/

# Expose service port
EXPOSE 50051

# Run service (adjust for RPC/gRPC)
CMD ["python", "services/service_a_story_generator.py"]
```

### Build Commands

```bash
# Build single service
docker build -f docker/Dockerfile.service-a -t pipeline/service-a:latest .

# Build all services
docker-compose build

# Build specific service
docker-compose build service-a
```

### Run Commands

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d service-a

# View logs
docker-compose logs -f service-a

# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Health Checks

Add health checks to containers:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:50051/health')"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Resource Limits

Set resource constraints per container:

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

## Logging

Configure logging for containers:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

Or use centralized logging (ELK, Fluentd, etc.).

## Notes

- **Communication Mode**: Containers can use either RPC or gRPC (configure via environment variables)
- **Data Persistence**: Use volumes for output files and logs
- **Security**: Don't expose unnecessary ports in production
- **Performance**: Monitor container resource usage during testing
- **Networking**: Ensure proper network configuration for multi-machine setups

## Testing Checklist

- [ ] All containers start successfully
- [ ] Services can communicate via Docker network
- [ ] Pipeline executes end-to-end
- [ ] Timestamps are correctly tracked across containers
- [ ] Output files are generated correctly
- [ ] Logs are accessible
- [ ] Performance metrics are comparable to local execution
- [ ] Resource usage is acceptable
- [ ] Containers restart correctly after failure

