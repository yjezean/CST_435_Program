#!/bin/bash
# Setup script for Machine 2 (Worker)
# This script prepares and starts services on the worker node

set -e  # Exit on error

echo "=========================================="
echo "Machine 2 Setup (Worker Node)"
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
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_info "Docker and Docker Compose are installed."

# Check if .env.machine2 exists
if [ ! -f .env.machine2 ]; then
    print_warning ".env.machine2 file not found. Using defaults."
else
    # Load environment variables
    export $(cat .env.machine2 | grep -v '^#' | xargs)
    print_info "Configuration loaded from .env.machine2"
fi

print_info "Pipeline Mode: ${PIPELINE_MODE:-grpc}"

# Get this machine's IP
MACHINE2_IP=$(hostname -I | awk '{print $1}')
print_info "This machine's IP: $MACHINE2_IP"
print_info "Machine 1 should use this IP in .env.machine1"

# Check firewall status
print_info "Checking firewall configuration..."
if command -v ufw &> /dev/null; then
    if sudo ufw status | grep -q "Status: active"; then
        print_warning "UFW firewall is active. Ensure ports 50053-50058 are open."
        print_info "Run: sudo ufw allow 50053:50058/tcp"
    fi
elif command -v firewall-cmd &> /dev/null; then
    if sudo firewall-cmd --state 2>/dev/null | grep -q "running"; then
        print_warning "Firewalld is active. Ensure ports 50053-50058 are open."
        print_info "Run: sudo firewall-cmd --permanent --add-port=50053-50058/tcp && sudo firewall-cmd --reload"
    fi
fi

# Build and start services
print_info "Building Docker images for Machine 2..."
docker-compose -f docker-compose.machine2.yaml build

print_info "Starting services on Machine 2..."
docker-compose -f docker-compose.machine2.yaml up -d

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 10

# Check service status
print_info "Checking service status..."
docker-compose -f docker-compose.machine2.yaml ps

# Verify services are listening
print_info "Verifying services are listening on ports..."

services=("service-c1:50053" "service-c2:50054" "service-c3:50055" "service-c4:50056" "service-c:50057" "service-d:50058")

for svc in "${services[@]}"; do
    svc_name="${svc%%:*}"
    port="${svc##*:}"
    
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        print_info "✓ ${svc_name} is listening on port $port"
    elif ss -tuln 2>/dev/null | grep -q ":$port "; then
        print_info "✓ ${svc_name} is listening on port $port"
    else
        print_warning "⚠ ${svc_name} may not be listening on port $port yet"
    fi
done

# Display logs
print_info "Recent logs from services:"
echo "----------------------------------------"
docker-compose -f docker-compose.machine2.yaml logs --tail=10

echo ""
echo "=========================================="
print_info "Machine 2 setup complete!"
echo "=========================================="
echo ""
print_info "Services are ready to receive requests from Machine 1"
print_info "This machine's IP: $MACHINE2_IP"
echo ""
print_info "To view logs:"
echo "  docker-compose -f docker-compose.machine2.yaml logs -f [service-name]"
echo ""
print_info "To stop services:"
echo "  docker-compose -f docker-compose.machine2.yaml down"
echo ""
print_info "Next steps:"
echo "  1. Note this machine's IP: $MACHINE2_IP"
echo "  2. On Machine 1, update .env.machine1 with MACHINE2_IP=$MACHINE2_IP"
echo "  3. On Machine 1, run: ./setup_machine1.sh"
echo ""
