#!/bin/bash

# Quick Start Script for Email Intelligence Collector - Comprehensive Analysis System
set -e

echo "🚀 Email Intelligence Collector - Comprehensive Analysis System"
echo "================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Desktop or Docker Compose plugin."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        log_warning ".env file not found. Creating from .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            log_success ".env file created"
        else
            log_error ".env.example file not found. Please check your project structure."
            exit 1
        fi
    else
        log_success ".env file found"
    fi
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    mkdir -p backend/logs
    mkdir -p backend/data
    mkdir -p backend/temp
    mkdir -p monitoring/dashboard
    log_success "Directories created"
}

# Build Docker images
build_images() {
    log_info "Building Docker images for comprehensive analysis..."
    docker compose -f docker-compose.comprehensive.yml build --no-cache
    if [ $? -eq 0 ]; then
        log_success "Docker images built successfully"
    else
        log_error "Failed to build Docker images"
        exit 1
    fi
}

# Start services
start_services() {
    log_info "Starting comprehensive analysis services..."
    docker compose -f docker-compose.comprehensive.yml up -d
    if [ $? -eq 0 ]; then
        log_success "Services started successfully"
    else
        log_error "Failed to start services"
        exit 1
    fi
}

# Wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    # Wait for database
    log_info "Waiting for database..."
    for i in {1..30}; do
        if docker compose -f docker-compose.comprehensive.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; then
            log_success "Database is ready"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # Wait for backend
    log_info "Waiting for backend..."
    for i in {1..60}; do
        if curl -sf http://localhost:8001/health > /dev/null 2>&1; then
            log_success "Backend is ready"
            break
        fi
        echo -n "."
        sleep 2
    done
}

# Test the system
test_system() {
    log_info "Testing comprehensive analysis system..."
    
    # Test health endpoint
    if curl -sf http://localhost:8001/health > /dev/null; then
        log_success "Health check passed"
    else
        log_warning "Health check failed, but services might still be starting"
    fi
    
    # Test comprehensive analysis endpoint
    log_info "Testing comprehensive analysis endpoint..."
    if python3 test_comprehensive_api.py > /dev/null 2>&1; then
        log_success "Comprehensive analysis API test passed"
    else
        log_warning "Comprehensive analysis API test failed - services might still be initializing"
    fi
}

# Display information
show_info() {
    echo ""
    echo "🎉 Comprehensive Analysis System Started Successfully!"
    echo "====================================================="
    echo ""
    echo "📊 Available Services:"
    echo "  • Backend API:           http://localhost:8001"
    echo "  • API Documentation:     http://localhost:8001/docs"
    echo "  • Frontend UI:           http://localhost:3001"
    echo "  • Monitoring Dashboard:  http://localhost:8080"
    echo "  • Database:              localhost:5433"
    echo "  • Redis Cache:           localhost:6380"
    echo "  • Elasticsearch:         http://localhost:9201"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs:             make comprehensive-logs"
    echo "  • Check status:          make comprehensive-status"
    echo "  • Run tests:             make comprehensive-test"
    echo "  • Run demo:              make comprehensive-demo"
    echo "  • Stop services:         make comprehensive-down"
    echo ""
    echo "🧪 Test the system:"
    echo "  curl -X POST 'http://localhost:8001/api/comprehensive-analysis' \\"
    echo "       -H 'Content-Type: application/json' \\"
    echo "       -d '{\"email\": \"buch1202@mail.ru\", \"force_refresh\": true}'"
    echo ""
    echo "📱 Demo scripts:"
    echo "  python3 test_comprehensive_api.py"
    echo "  python3 demo_comprehensive_analysis.py"
    echo ""
}

# Cleanup on exit
cleanup() {
    if [ $? -ne 0 ]; then
        log_error "Setup failed. Check the logs for details."
        log_info "To view logs: make comprehensive-logs"
        log_info "To stop services: make comprehensive-down"
    fi
}

trap cleanup EXIT

# Main execution
main() {
    check_prerequisites
    check_env_file
    create_directories
    build_images
    start_services
    wait_for_services
    test_system
    show_info
}

# Execute main function
main "$@"
