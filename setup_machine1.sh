#!/bin/bash
# Setup script for Machine 1 (Controller)
# This script prepares and starts services on the controller node

set -e  # Exit on error

echo "=========================================="
echo "Machine 1 Setup (Controller Node)"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_info "Docker and Docker Compose are installed."

# Check if .env.machine1 exists
if [ ! -f .env.machine1 ]; then
    print_error ".env.machine1 file not found!"
    print_error "Please create .env.machine1 and set MACHINE2_IP"
    exit 1
fi

# Load environment variables
export $(cat .env.machine1 | grep -v '^#' | xargs)

# Check if MACHINE2_IP is set
if [ -z "$MACHINE2_IP" ]; then
    print_error "MACHINE2_IP is not set in .env.machine1"
    print_error "Please update .env.machine1 with Machine 2's IP address"
    exit 1
fi

print_info "Configuration loaded from .env.machine1"
print_info "Machine 2 IP: $MACHINE2_IP"
print_info "Pipeline Mode: ${PIPELINE_MODE:-grpc}"

# Get this machine's IP
MACHINE1_IP=$(hostname -I | awk '{print $1}')
print_info "This machine's IP: $MACHINE1_IP"

# Test connectivity to Machine 2
print_info "Testing connectivity to Machine 2..."
if ping -c 2 -W 2 $MACHINE2_IP &> /dev/null; then
    print_info "✓ Machine 2 is reachable at $MACHINE2_IP"
else
    print_warning "⚠ Cannot ping Machine 2 at $MACHINE2_IP"
    print_warning "This might be normal if ICMP is blocked. Continuing..."
fi

# Check if Machine 2 services are running
print_info "Checking if Machine 2 services are available..."
if command -v nc &> /dev/null; then
    if nc -z -w 2 $MACHINE2_IP 50057 2>/dev/null; then
        print_info "✓ Service C is reachable on Machine 2"
    else
        print_warning "⚠ Service C (port 50057) not reachable on Machine 2"
        print_warning "Make sure services are started on Machine 2 first!"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Build and start services
print_info "Building Docker images for Machine 1..."
docker-compose -f docker-compose.machine1.yaml build

print_info "Starting services on Machine 1..."
docker-compose -f docker-compose.machine1.yaml up -d

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 5

# Check service status
print_info "Checking service status..."
docker-compose -f docker-compose.machine1.yaml ps

# Verify services are listening
print_info "Verifying services are listening on ports..."
if docker exec story-generator-machine1 python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 50051)); s.close()" 2>/dev/null; then
    print_info "✓ Service A is listening on port 50051"
else
    print_error "✗ Service A is not responding"
fi

if docker exec story-analyzer-machine1 python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 50052)); s.close()" 2>/dev/null; then
    print_info "✓ Service B is listening on port 50052"
else
    print_error "✗ Service B is not responding"
fi

# Display logs
print_info "Recent logs from services:"
echo "----------------------------------------"
docker-compose -f docker-compose.machine1.yaml logs --tail=10

echo ""
echo "=========================================="
print_info "Machine 1 setup complete!"
echo "=========================================="
echo ""
print_info "To run the pipeline:"
echo "  docker-compose -f docker-compose.machine1.yaml exec service-main python main.py \"Your story prompt\""
echo ""
print_info "To view logs:"
echo "  docker-compose -f docker-compose.machine1.yaml logs -f"
echo ""
print_info "To stop services:"
echo "  docker-compose -f docker-compose.machine1.yaml down"
echo ""
