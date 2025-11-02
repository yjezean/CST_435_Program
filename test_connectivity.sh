#!/bin/bash
# Test connectivity between Machine 1 and Machine 2
# Run this script on Machine 1 after both machines are set up

set -e

echo "=========================================="
echo "Distributed Deployment Connectivity Test"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Load environment
if [ -f .env.machine1 ]; then
    export $(cat .env.machine1 | grep -v '^#' | xargs)
else
    print_error ".env.machine1 not found"
    exit 1
fi

if [ -z "$MACHINE2_IP" ]; then
    print_error "MACHINE2_IP not set in .env.machine1"
    exit 1
fi

print_info "Testing connectivity to Machine 2 at $MACHINE2_IP"
echo ""

# Test 1: Network connectivity
print_info "Test 1: Network connectivity (ping)"
if ping -c 3 -W 2 $MACHINE2_IP &> /dev/null; then
    print_success "✓ Machine 2 is reachable"
else
    print_error "✗ Cannot ping Machine 2 (may be normal if ICMP is blocked)"
fi
echo ""

# Test 2: Port connectivity
print_info "Test 2: Port connectivity"

ports=("50053:Service C1" "50054:Service C2" "50055:Service C3" "50056:Service C4" "50057:Service C" "50058:Service D")

all_ports_ok=true

for port_info in "${ports[@]}"; do
    port="${port_info%%:*}"
    service="${port_info##*:}"
    
    if command -v nc &> /dev/null; then
        if nc -z -w 2 $MACHINE2_IP $port 2>/dev/null; then
            print_success "✓ $service (port $port) is reachable"
        else
            print_error "✗ $service (port $port) is NOT reachable"
            all_ports_ok=false
        fi
    elif command -v telnet &> /dev/null; then
        if timeout 2 telnet $MACHINE2_IP $port 2>/dev/null | grep -q "Connected"; then
            print_success "✓ $service (port $port) is reachable"
        else
            print_error "✗ $service (port $port) is NOT reachable"
            all_ports_ok=false
        fi
    else
        print_error "Neither nc nor telnet is available. Cannot test ports."
        break
    fi
done
echo ""

# Test 3: Local services
print_info "Test 3: Local services on Machine 1"

if docker ps | grep -q story-generator-machine1; then
    if docker exec story-generator-machine1 python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 50051)); s.close()" 2>/dev/null; then
        print_success "✓ Service A (Story Generator) is running"
    else
        print_error "✗ Service A is not responding"
        all_ports_ok=false
    fi
else
    print_error "✗ Service A container is not running"
    all_ports_ok=false
fi

if docker ps | grep -q story-analyzer-machine1; then
    if docker exec story-analyzer-machine1 python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 50052)); s.close()" 2>/dev/null; then
        print_success "✓ Service B (Story Analyzer) is running"
    else
        print_error "✗ Service B is not responding"
        all_ports_ok=false
    fi
else
    print_error "✗ Service B container is not running"
    all_ports_ok=false
fi

if docker ps | grep -q main-machine1; then
    print_success "✓ Main program container is running"
else
    print_error "✗ Main program container is not running"
    all_ports_ok=false
fi

echo ""

# Test 4: Try a simple connection test
print_info "Test 4: Testing gRPC/RPC connection"

MODE=${PIPELINE_MODE:-grpc}

if [ "$MODE" = "grpc" ]; then
    print_info "Testing gRPC connection to Service C..."
    # Simple Python test using grpc
    docker exec main-machine1 python -c "
import socket
import sys
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    s.connect(('$MACHINE2_IP', 50057))
    s.close()
    print('gRPC endpoint reachable')
    sys.exit(0)
except Exception as e:
    print(f'gRPC endpoint not reachable: {e}')
    sys.exit(1)
" && print_success "✓ gRPC connection to Service C successful" || print_error "✗ gRPC connection failed"
else
    print_info "Testing RPC connection to Service C..."
    docker exec main-machine1 python -c "
import socket
import sys
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    s.connect(('$MACHINE2_IP', 8057))
    s.close()
    print('RPC endpoint reachable')
    sys.exit(0)
except Exception as e:
    print(f'RPC endpoint not reachable: {e}')
    sys.exit(1)
" && print_success "✓ RPC connection to Service C successful" || print_error "✗ RPC connection failed"
fi

echo ""
echo "=========================================="

if [ "$all_ports_ok" = true ]; then
    print_success "All tests passed! Ready to run the pipeline."
    echo ""
    print_info "To run the pipeline:"
    echo "  docker-compose -f docker-compose.machine1.yaml exec service-main python main.py \"Your story prompt\""
else
    print_error "Some tests failed. Please check the configuration."
    echo ""
    print_info "Troubleshooting steps:"
    echo "  1. Ensure Machine 2 services are running"
    echo "  2. Check firewall rules on both machines"
    echo "  3. Verify IP addresses in .env.machine1"
    echo "  4. Check service logs: docker-compose logs"
fi

echo "=========================================="
