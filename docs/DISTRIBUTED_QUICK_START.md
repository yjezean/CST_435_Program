# Distributed Deployment Quick Start Guide

This is a streamlined guide to get your distributed pipeline running across 2 machines.

## Prerequisites

Both machines must have:
- Docker and Docker Compose installed
- Network connectivity to each other
- Open firewall ports (50051-50058)

## Quick Setup (5 Steps)

### Step 1: Get IP Addresses

**On Machine 2:**
```bash
hostname -I
```
Note the IP address (e.g., 192.168.1.20)

**On Machine 1:**
```bash
hostname -I
```
Note the IP address (e.g., 192.168.1.10)

### Step 2: Clone Repository on Both Machines

```bash
# On both machines
cd ~/workspace
git clone <your-repo-url> CST_435_Program
cd CST_435_Program
```

### Step 3: Configure Machine 1

**Edit `.env.machine1` and update MACHINE2_IP:**

```bash
nano .env.machine1
```

Change:
```
MACHINE2_IP=192.168.1.20  # Replace with Machine 2's actual IP
```

### Step 4: Start Services (Machine 2 FIRST!)

**On Machine 2:**
```bash
chmod +x setup_machine2.sh
./setup_machine2.sh
```

Wait until you see "Machine 2 setup complete!"

**On Machine 1:**
```bash
chmod +x setup_machine1.sh
./setup_machine1.sh
```

### Step 5: Run the Pipeline

**On Machine 1:**
```bash
# Test connectivity first
chmod +x test_connectivity.sh
./test_connectivity.sh

# If all tests pass, run the pipeline:
docker-compose -f docker-compose.machine1.yaml exec service-main python main.py "A space adventure about robots"
```

## Switching Between RPC and gRPC

### For gRPC Mode (Default)

**Machine 2:**
```bash
docker-compose -f docker-compose.machine2.yaml down
PIPELINE_MODE=grpc docker-compose -f docker-compose.machine2.yaml up -d
```

**Machine 1:**
```bash
docker-compose -f docker-compose.machine1.yaml down
PIPELINE_MODE=grpc docker-compose -f docker-compose.machine1.yaml up -d
```

### For RPC Mode

**Machine 2:**
```bash
docker-compose -f docker-compose.machine2.yaml down
PIPELINE_MODE=rpc docker-compose -f docker-compose.machine2.yaml up -d
```

**Machine 1:**
```bash
docker-compose -f docker-compose.machine1.yaml down
PIPELINE_MODE=rpc docker-compose -f docker-compose.machine1.yaml up -d
```

## Common Commands

### View Logs

```bash
# Machine 1
docker-compose -f docker-compose.machine1.yaml logs -f

# Machine 2
docker-compose -f docker-compose.machine2.yaml logs -f
```

### Check Service Status

```bash
# Machine 1
docker-compose -f docker-compose.machine1.yaml ps

# Machine 2
docker-compose -f docker-compose.machine2.yaml ps
```

### Restart Services

```bash
# Machine 1
docker-compose -f docker-compose.machine1.yaml restart

# Machine 2
docker-compose -f docker-compose.machine2.yaml restart
```

### Stop All Services

```bash
# Machine 1
docker-compose -f docker-compose.machine1.yaml down

# Machine 2
docker-compose -f docker-compose.machine2.yaml down
```

## Firewall Configuration

### Ubuntu/Debian (ufw)

**Machine 1:**
```bash
sudo ufw allow 50051:50052/tcp
```

**Machine 2:**
```bash
sudo ufw allow 50053:50058/tcp
```

### RHEL/CentOS (firewalld)

**Machine 1:**
```bash
sudo firewall-cmd --permanent --add-port=50051-50052/tcp
sudo firewall-cmd --reload
```

**Machine 2:**
```bash
sudo firewall-cmd --permanent --add-port=50053-50058/tcp
sudo firewall-cmd --reload
```

## Troubleshooting

### Problem: "Cannot connect to Machine 2"

**Solution:**
1. Verify Machine 2 services are running: `docker ps`
2. Check firewall: `sudo ufw status` or `sudo firewall-cmd --list-all`
3. Test connectivity: `ping <MACHINE2_IP>`
4. Test ports: `nc -zv <MACHINE2_IP> 50057`

### Problem: "Connection timeout"

**Solution:**
1. Ensure services are listening on 0.0.0.0, not 127.0.0.1
2. Check Docker network mode (should be host or bridge with port mapping)
3. Verify environment variables in .env files

### Problem: "Service not found"

**Solution:**
1. Check service names in docker-compose files
2. Ensure all services are running: `docker-compose ps`
3. Check logs for errors: `docker-compose logs <service-name>`

### Problem: "Permission denied" on scripts

**Solution:**
```bash
chmod +x setup_machine1.sh setup_machine2.sh test_connectivity.sh
```

## Performance Testing

To compare performance between local, Docker, and distributed:

1. **Local mode** (baseline):
   ```bash
   python main.py "test story"
   ```

2. **Local Docker** (all services on one machine):
   ```bash
   docker-compose up -d
   docker-compose exec service-main python main.py "test story"
   ```

3. **Distributed** (across 2 machines):
   ```bash
   # After setup
   docker-compose -f docker-compose.machine1.yaml exec service-main python main.py "test story"
   ```

Compare the output files:
- `output/pipeline_output_local.json`
- `output/pipeline_output_local_docker_grpc.json`
- Check timestamps in each file

## Architecture Diagram

```
Machine 1 (Controller)                    Machine 2 (Worker)
┌─────────────────────┐                  ┌──────────────────────┐
│  Main Program       │                  │                      │
│  (Orchestrator)     │                  │                      │
└──────────┬──────────┘                  │                      │
           │                              │                      │
┌──────────▼──────────┐                  │                      │
│  Service A          │                  │                      │
│  (Story Generator)  │                  │                      │
└──────────┬──────────┘                  │                      │
           │                              │                      │
┌──────────▼──────────┐                  │                      │
│  Service B          │                  │                      │
│  (Story Analyzer)   │                  │                      │
└──────────┬──────────┘                  │                      │
           │                              │                      │
           │        Network Connection    │                      │
           └─────────────────────────────►│  Service C          │
                      (gRPC/RPC)          │  (Parallel Hub)     │
                                          └──────┬──────────────┘
                                                 │
                              ┌──────────────────┼──────────────────┐
                              │                  │                  │
                   ┌──────────▼─────┐ ┌─────────▼────┐ ┌─────────▼────┐
                   │  Service C1    │ │ Service C2   │ │ Service C3   │
                   │  (Image)       │ │ (Audio)      │ │ (Translation)│
                   └────────────────┘ └──────────────┘ └──────────────┘
                              │
                   ┌──────────▼─────┐
                   │  Service C4    │
                   │  (Formatting)  │
                   └────────┬───────┘
                            │
                   ┌────────▼───────┐
                   │  Service D     │
                   │  (Aggregator)  │◄────────────────┐
                   └────────┬───────┘                 │
                            │                          │
                            └──────────────────────────┘
                                 (Result returned to Main)
```

## Next Steps

1. Run the pipeline with different prompts
2. Compare performance between RPC and gRPC
3. Monitor network traffic and latency
4. Experiment with different service distributions
5. Try running parallel services (C1-C4) on separate machines

## Support

For detailed information, see:
- `docs/distributed_deployment.md` - Full deployment guide
- `docker-compose.machine1.yaml` - Machine 1 configuration
- `docker-compose.machine2.yaml` - Machine 2 configuration
- `.env.machine1` - Machine 1 environment variables
- `.env.machine2` - Machine 2 environment variables
