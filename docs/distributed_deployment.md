# Distributed Deployment Guide - Two Machine Setup

This guide explains how to deploy the AI Story Creator Pipeline across two machines using both RPC and gRPC protocols.

## Architecture Overview

The services are split across two machines for distributed processing:

### Machine 1 (Primary/Controller)
- Main Program (orchestrator)
- Service A (Story Generator)
- Service B (Story Analyzer)

### Machine 2 (Worker/Parallel Processor)
- Service C (Parallel Hub)
- Service C1 (Image Concept)
- Service C2 (Audio Script)
- Service C3 (Translation)
- Service C4 (Formatting)
- Service D (Aggregator)

## Network Requirements

### Prerequisites
1. Both machines must be on the same network (or accessible via public IPs)
2. Firewall rules must allow traffic on required ports
3. Docker and Docker Compose installed on both machines
4. Git installed to clone the repository

### Required Ports

#### Machine 1 Ports (open these on firewall):
- **50051**: Service A (gRPC)
- **50052**: Service B (gRPC)
- **8051**: Service A (RPC fallback)
- **8052**: Service B (RPC fallback)

#### Machine 2 Ports (open these on firewall):
- **50053**: Service C1 (gRPC)
- **50054**: Service C2 (gRPC)
- **50055**: Service C3 (gRPC)
- **50056**: Service C4 (gRPC)
- **50057**: Service C (gRPC)
- **50058**: Service D (gRPC)
- **8053-8058**: RPC fallback ports

## Setup Instructions

### Step 1: Network Configuration

On each machine, find its IP address:

```bash
# Linux
ip addr show | grep inet

# Or use:
hostname -I
```

Record the IP addresses:
- Machine 1 IP: `_____._____._____.____` (example: 192.168.1.10)
- Machine 2 IP: `_____._____._____.____` (example: 192.168.1.20)

### Step 2: Clone Repository on Both Machines

```bash
# On both machines
git clone <repository-url>
cd CST_435_Program
```

### Step 3: Configure Environment Variables

#### Machine 1 Configuration

Create `.env.machine1` file:

```bash
# Machine 1 Environment Configuration
# Replace MACHINE2_IP with actual IP address of Machine 2

# This machine's services
SERVICE_A_HOST=0.0.0.0
SERVICE_A_PORT=50051
SERVICE_B_HOST=0.0.0.0
SERVICE_B_PORT=50052

# Remote services on Machine 2 (update with actual IP)
MACHINE2_IP=192.168.1.20
SERVICE_C_HOST=${MACHINE2_IP}
SERVICE_C_PORT=50057
SERVICE_D_HOST=${MACHINE2_IP}
SERVICE_D_PORT=50058

# Pipeline mode (grpc or rpc)
PIPELINE_MODE=grpc
```

#### Machine 2 Configuration

Create `.env.machine2` file:

```bash
# Machine 2 Environment Configuration
# Replace MACHINE1_IP with actual IP address of Machine 1

MACHINE1_IP=192.168.1.10

# Parallel services
C1_HOST=0.0.0.0
C1_PORT=50053
C2_HOST=0.0.0.0
C2_PORT=50054
C3_HOST=0.0.0.0
C3_PORT=50055
C4_HOST=0.0.0.0
C4_PORT=50056

# Hub and Aggregator
SERVICE_C_HOST=0.0.0.0
SERVICE_C_PORT=50057
SERVICE_D_HOST=0.0.0.0
SERVICE_D_PORT=50058

# For service C to communicate with C1-C4
SERVICE_C1_HOST=service-c1
SERVICE_C2_HOST=service-c2
SERVICE_C3_HOST=service-c3
SERVICE_C4_HOST=service-c4

# Pipeline mode (grpc or rpc)
PIPELINE_MODE=grpc
```

### Step 4: Launch Services

#### On Machine 2 (Start Worker Services First)

```bash
# For gRPC mode
docker-compose -f docker-compose.machine2.yaml up -d

# For RPC mode
PIPELINE_MODE=rpc docker-compose -f docker-compose.machine2.yaml up -d
```

Verify services are running:
```bash
docker-compose -f docker-compose.machine2.yaml ps
```

Test connectivity:
```bash
# Test if services are listening
netstat -tuln | grep -E "50053|50054|50055|50056|50057|50058"
```

#### On Machine 1 (Start Controller Services)

Update the `.env.machine1` file with Machine 2's actual IP, then:

```bash
# For gRPC mode
docker-compose -f docker-compose.machine1.yaml up -d

# For RPC mode
PIPELINE_MODE=rpc docker-compose -f docker-compose.machine1.yaml up -d
```

Verify services:
```bash
docker-compose -f docker-compose.machine1.yaml ps
```

### Step 5: Run the Main Program

On Machine 1:

```bash
# Using Docker (recommended)
docker-compose -f docker-compose.machine1.yaml exec service-main python main.py "A space adventure"

# Or run locally (requires setting environment variables)
export MACHINE2_IP=192.168.1.20
export SERVICE_A_HOST=localhost
export SERVICE_B_HOST=localhost
export SERVICE_C_HOST=${MACHINE2_IP}
export SERVICE_D_HOST=${MACHINE2_IP}
export PIPELINE_MODE=grpc
python main.py "A space adventure"
```

## Switching Between RPC and gRPC

### For gRPC Mode
```bash
# Machine 2
PIPELINE_MODE=grpc docker-compose -f docker-compose.machine2.yaml up -d

# Machine 1
PIPELINE_MODE=grpc docker-compose -f docker-compose.machine1.yaml up -d
```

### For RPC Mode
```bash
# Machine 2
PIPELINE_MODE=rpc docker-compose -f docker-compose.machine2.yaml up -d

# Machine 1
PIPELINE_MODE=rpc docker-compose -f docker-compose.machine1.yaml up -d
```

## Firewall Configuration

### Ubuntu/Debian (ufw)

```bash
# On Machine 1
sudo ufw allow 50051/tcp  # Service A
sudo ufw allow 50052/tcp  # Service B
sudo ufw allow 8051/tcp   # Service A RPC
sudo ufw allow 8052/tcp   # Service B RPC

# On Machine 2
sudo ufw allow 50053/tcp  # Service C1
sudo ufw allow 50054/tcp  # Service C2
sudo ufw allow 50055/tcp  # Service C3
sudo ufw allow 50056/tcp  # Service C4
sudo ufw allow 50057/tcp  # Service C
sudo ufw allow 50058/tcp  # Service D
sudo ufw allow 8053:8058/tcp  # RPC ports
```

### RHEL/CentOS (firewalld)

```bash
# On Machine 1
sudo firewall-cmd --permanent --add-port=50051-50052/tcp
sudo firewall-cmd --permanent --add-port=8051-8052/tcp
sudo firewall-cmd --reload

# On Machine 2
sudo firewall-cmd --permanent --add-port=50053-50058/tcp
sudo firewall-cmd --permanent --add-port=8053-8058/tcp
sudo firewall-cmd --reload
```

## Testing Connectivity

### Test from Machine 1 to Machine 2

```bash
# Test network connectivity
ping <MACHINE2_IP>

# Test port connectivity (requires telnet or nc)
nc -zv <MACHINE2_IP> 50057
nc -zv <MACHINE2_IP> 50058

# Test from inside a container
docker run --rm -it busybox telnet <MACHINE2_IP> 50057
```

### Test from Machine 2 to Machine 1

```bash
# Test network connectivity
ping <MACHINE1_IP>

# Test port connectivity
nc -zv <MACHINE1_IP> 50051
nc -zv <MACHINE1_IP> 50052
```

## Troubleshooting

### Services Can't Connect

1. **Check firewall rules**: Ensure all ports are open
2. **Check service status**: `docker-compose ps` on both machines
3. **Check logs**: `docker-compose logs <service-name>`
4. **Verify IP addresses**: Ensure environment variables have correct IPs
5. **Test network connectivity**: Use ping and telnet/nc

### Connection Timeout

```bash
# Check if service is listening on the correct interface
docker exec <container-name> netstat -tuln

# Should show 0.0.0.0:<port> not 127.0.0.1:<port>
```

### DNS Issues

If using hostnames instead of IPs, ensure DNS resolution works:
```bash
nslookup <hostname>
```

### Container Networking Issues

```bash
# Check Docker network
docker network inspect bridge

# Ensure containers are using host network for external communication
# Or configure proper bridge networking with exposed ports
```

## Performance Comparison

Compare performance across different deployment modes:

1. **Local (baseline)**: All services in one process
2. **Local Docker**: All services in Docker on one machine
3. **Distributed**: Services across two machines

Example metrics to collect:
- Total pipeline execution time
- Network latency between machines
- Individual service execution times
- Parallel processing efficiency

## Advanced Configuration

### Using Custom Networks

For better isolation, create custom Docker networks:

```bash
# Machine 1
docker network create pipeline-net-machine1

# Machine 2
docker network create pipeline-net-machine2
```

### Load Balancing

For high availability, consider:
- Running multiple instances of parallel services (C1-C4)
- Using nginx or HAProxy for load balancing
- Implementing service discovery (Consul, etcd)

### Security

For production deployments:
1. Use TLS/SSL for gRPC connections
2. Implement authentication tokens
3. Use VPN for inter-machine communication
4. Encrypt sensitive data in transit

## Monitoring

### Container Health

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f <service-name>

# Check resource usage
docker stats
```

### Network Monitoring

```bash
# Monitor network connections
netstat -anp | grep :5005

# Check bandwidth usage
iftop

# Monitor latency
ping -c 10 <MACHINE2_IP>
```

## Cleanup

### Stop Services

```bash
# Machine 1
docker-compose -f docker-compose.machine1.yaml down

# Machine 2
docker-compose -f docker-compose.machine2.yaml down
```

### Remove All Containers and Images

```bash
# On both machines
docker-compose down --rmi all --volumes
```

## Next Steps

1. Review the generated `docker-compose.machine1.yaml` and `docker-compose.machine2.yaml` files
2. Update IP addresses in environment configuration
3. Start services on Machine 2 first
4. Start services on Machine 1
5. Run the pipeline and compare performance
6. Experiment with RPC vs gRPC modes

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Verify network connectivity
3. Ensure all environment variables are set correctly
4. Review firewall configurations
