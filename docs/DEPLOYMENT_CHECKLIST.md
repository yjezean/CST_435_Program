# Distributed Deployment Checklist

Use this checklist to ensure proper setup of distributed deployment across 2 machines.

## Pre-Deployment

### Both Machines
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Git installed (`git --version`)
- [ ] Network connectivity between machines
- [ ] Sufficient disk space (5GB minimum)
- [ ] Sufficient RAM (4GB minimum per machine)

### Network Information
- [ ] Machine 1 IP Address: `_____._____._____.______`
- [ ] Machine 2 IP Address: `_____._____._____.______`
- [ ] Machines can ping each other
- [ ] No corporate proxy blocking connections

## Machine 2 Setup (Worker Node)

### Initial Setup
- [ ] Clone repository: `git clone <repo-url>`
- [ ] Navigate to project: `cd CST_435_Program`
- [ ] Review `.env.machine2` configuration
- [ ] Verify firewall ports are open (50053-50058)

### Service Deployment
- [ ] Run setup script: `./setup_machine2.sh`
- [ ] All services show "Up" in `docker-compose ps`
- [ ] No error messages in setup output
- [ ] Services are listening on expected ports
- [ ] Health checks passing

### Verification
- [ ] Service C1 accessible on port 50053
- [ ] Service C2 accessible on port 50054
- [ ] Service C3 accessible on port 50055
- [ ] Service C4 accessible on port 50056
- [ ] Service C hub accessible on port 50057
- [ ] Service D accessible on port 50058
- [ ] No errors in logs: `docker-compose -f docker-compose.machine2.yaml logs`

## Machine 1 Setup (Controller Node)

### Initial Setup
- [ ] Clone repository: `git clone <repo-url>`
- [ ] Navigate to project: `cd CST_435_Program`
- [ ] Edit `.env.machine1`
- [ ] Set MACHINE2_IP to Machine 2's IP address
- [ ] Verify firewall ports are open (50051-50052)

### Service Deployment
- [ ] Run setup script: `./setup_machine1.sh`
- [ ] All services show "Up" in `docker-compose ps`
- [ ] No error messages in setup output
- [ ] Services can reach Machine 2
- [ ] Health checks passing

### Verification
- [ ] Service A accessible on port 50051
- [ ] Service B accessible on port 50052
- [ ] Main container is running
- [ ] No errors in logs: `docker-compose -f docker-compose.machine1.yaml logs`

## Connectivity Testing

### Network Tests
- [ ] Run connectivity test: `./test_connectivity.sh`
- [ ] Machine 2 is reachable (ping test)
- [ ] All ports are accessible (port test)
- [ ] Local services responding (service test)
- [ ] gRPC/RPC connection successful

### Manual Tests
- [ ] Can telnet to Machine 2 ports: `nc -zv <MACHINE2_IP> 50057`
- [ ] Can telnet to Machine 1 ports: `nc -zv <MACHINE1_IP> 50051`
- [ ] DNS resolution working (if using hostnames)

## Firewall Configuration

### Machine 1 Firewall
- [ ] Port 50051 open (Service A)
- [ ] Port 50052 open (Service B)
- [ ] Port 8051 open (RPC fallback)
- [ ] Port 8052 open (RPC fallback)

### Machine 2 Firewall
- [ ] Ports 50053-50058 open (all services)
- [ ] Ports 8053-8058 open (RPC fallback)
- [ ] Firewall rules saved/persistent

#### Ubuntu/Debian Commands
```bash
# Machine 1
sudo ufw allow 50051:50052/tcp
sudo ufw allow 8051:8052/tcp

# Machine 2
sudo ufw allow 50053:50058/tcp
sudo ufw allow 8053:8058/tcp
```

#### RHEL/CentOS Commands
```bash
# Machine 1
sudo firewall-cmd --permanent --add-port=50051-50052/tcp
sudo firewall-cmd --permanent --add-port=8051-8052/tcp
sudo firewall-cmd --reload

# Machine 2
sudo firewall-cmd --permanent --add-port=50053-50058/tcp
sudo firewall-cmd --permanent --add-port=8053-8058/tcp
sudo firewall-cmd --reload
```

## Pipeline Execution

### gRPC Mode
- [ ] Services running in gRPC mode on both machines
- [ ] Run pipeline: `docker-compose -f docker-compose.machine1.yaml exec service-main python main.py "test prompt"`
- [ ] Pipeline completes successfully
- [ ] Output file generated: `output/pipeline_output_local_docker_grpc.json`
- [ ] Timestamps look reasonable
- [ ] No errors in output

### RPC Mode
- [ ] Switch Machine 2 to RPC: `PIPELINE_MODE=rpc docker-compose -f docker-compose.machine2.yaml up -d`
- [ ] Switch Machine 1 to RPC: `PIPELINE_MODE=rpc docker-compose -f docker-compose.machine1.yaml up -d`
- [ ] Run pipeline: `docker-compose -f docker-compose.machine1.yaml exec service-main python main.py "test prompt"`
- [ ] Pipeline completes successfully
- [ ] Output file generated: `output/pipeline_output_local_docker_rpc.json`
- [ ] Timestamps look reasonable
- [ ] No errors in output

## Performance Testing

### Baseline Tests
- [ ] Local mode execution time recorded
- [ ] Local Docker gRPC execution time recorded
- [ ] Local Docker RPC execution time recorded
- [ ] Distributed gRPC execution time recorded
- [ ] Distributed RPC execution time recorded

### Comparison
- [ ] Run comparison script: `./compare_performance.sh "test prompt"`
- [ ] All modes complete successfully
- [ ] Performance table generated
- [ ] Results documented
- [ ] Network overhead measured

### Performance Expectations
- [ ] Distributed time >= Local Docker time (network overhead expected)
- [ ] Network latency between machines measured
- [ ] No unexpectedly slow services
- [ ] Parallel services showing true parallelism

## Output Verification

### File Generation
- [ ] `output/pipeline_output_local.json` exists (if tested locally)
- [ ] `output/pipeline_output_local_docker_grpc.json` exists
- [ ] `output/pipeline_output_local_docker_rpc.json` exists
- [ ] Files are valid JSON
- [ ] Files contain all expected sections

### Content Verification
- [ ] Story text present and complete
- [ ] Analysis data present
- [ ] Image concept generated
- [ ] Audio script generated
- [ ] Translations present (Spanish, French)
- [ ] Formatted outputs present (Markdown, HTML)
- [ ] All timestamps populated
- [ ] Execution mode correctly identified

## Troubleshooting (If Issues Occur)

### Connection Issues
- [ ] Checked IP addresses are correct
- [ ] Verified firewall rules
- [ ] Tested network connectivity
- [ ] Checked service logs
- [ ] Verified port bindings

### Service Issues
- [ ] Checked Docker daemon status
- [ ] Verified sufficient resources
- [ ] Checked environment variables
- [ ] Reviewed container logs
- [ ] Verified image builds successful

### Performance Issues
- [ ] Checked network latency
- [ ] Monitored CPU usage
- [ ] Monitored memory usage
- [ ] Checked for errors in logs
- [ ] Verified no throttling

## Documentation

### Understanding
- [ ] Read `docs/DISTRIBUTED_QUICK_START.md`
- [ ] Read `docs/distributed_deployment.md`
- [ ] Read `docs/DISTRIBUTED_IMPLEMENTATION_SUMMARY.md`
- [ ] Understand architecture diagram
- [ ] Understand service split between machines

### Results
- [ ] Performance results documented
- [ ] Screenshots captured (optional)
- [ ] Any issues documented
- [ ] Lessons learned noted

## Cleanup (When Done)

### Machine 1
- [ ] Stop services: `docker-compose -f docker-compose.machine1.yaml down`
- [ ] Remove volumes (optional): `docker-compose -f docker-compose.machine1.yaml down -v`
- [ ] Remove images (optional): `docker-compose -f docker-compose.machine1.yaml down --rmi all`

### Machine 2
- [ ] Stop services: `docker-compose -f docker-compose.machine2.yaml down`
- [ ] Remove volumes (optional): `docker-compose -f docker-compose.machine2.yaml down -v`
- [ ] Remove images (optional): `docker-compose -f docker-compose.machine2.yaml down --rmi all`

## Final Status

Date Completed: _______________

### Summary
- [ ] All services deployed successfully
- [ ] Both gRPC and RPC modes tested
- [ ] Performance comparison completed
- [ ] Results documented
- [ ] Ready for presentation/submission

### Notes
```
_____________________________________________________________________________

_____________________________________________________________________________

_____________________________________________________________________________

_____________________________________________________________________________
```

---

## Quick Reference Commands

### Check Status
```bash
# Machine 1
docker-compose -f docker-compose.machine1.yaml ps

# Machine 2
docker-compose -f docker-compose.machine2.yaml ps
```

### View Logs
```bash
# Machine 1
docker-compose -f docker-compose.machine1.yaml logs -f [service-name]

# Machine 2
docker-compose -f docker-compose.machine2.yaml logs -f [service-name]
```

### Restart Services
```bash
# Machine 1
docker-compose -f docker-compose.machine1.yaml restart

# Machine 2
docker-compose -f docker-compose.machine2.yaml restart
```

### Test Connectivity
```bash
# From Machine 1
./test_connectivity.sh

# Manual port test
nc -zv <MACHINE2_IP> 50057
```

### Run Pipeline
```bash
# On Machine 1
docker-compose -f docker-compose.machine1.yaml exec service-main python main.py "Your story prompt"
```

---

**Tip**: Keep this checklist handy during setup. Check off items as you complete them to ensure nothing is missed!
