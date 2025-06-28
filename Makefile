# Email Intelligence Collector - Docker Management

.PHONY: help build up down logs clean dev-up dev-down test

# Default target
help:
	@echo "Email Intelligence Collector - Docker Commands"
	@echo ""
	@echo "Production Commands:"
	@echo "  make build         - Build all Docker images"
	@echo "  make up            - Start all services in production mode"
	@echo "  make down          - Stop all services"
	@echo "  make restart       - Restart all services"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev-build     - Build development images"
	@echo "  make dev-up        - Start services in development mode"
	@echo "  make dev-down      - Stop development services"
	@echo "  make dev-restart   - Restart development services"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make logs          - View logs from all services"
	@echo "  make logs-backend  - View backend logs"
	@echo "  make logs-frontend - View frontend logs"
	@echo "  make clean         - Remove all containers, volumes, and images"
	@echo "  make reset         - Complete reset (clean + rebuild)"
	@echo "  make shell-backend - Access backend container shell"
	@echo "  make shell-db      - Access database shell"
	@echo "  make test          - Run tests"
	@echo ""

# Production Commands
build:
	@echo "Building production images..."
	docker-compose build --no-cache

up:
	@echo "Starting production services..."
	docker-compose up -d

down:
	@echo "Stopping all services..."
	docker-compose down

restart: down up
	@echo "Services restarted"

# Development Commands
dev-build:
	@echo "Building development images..."
	docker-compose -f docker-compose.dev.yml build --no-cache

dev-up:
	@echo "Starting development services..."
	docker-compose -f docker-compose.dev.yml up -d

dev-down:
	@echo "Stopping development services..."
	docker-compose -f docker-compose.dev.yml down

dev-restart: dev-down dev-up
	@echo "Development services restarted"

# Utility Commands
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f db

shell-backend:
	docker-compose exec backend /bin/bash

shell-db:
	docker-compose exec db psql -U postgres -d eic_db

clean:
	@echo "Cleaning up containers, volumes, and images..."
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f
	docker volume prune -f

reset: clean build
	@echo "Complete reset completed"

# Database Commands
db-migrate:
	docker-compose exec backend alembic upgrade head

db-reset:
	docker-compose exec backend alembic downgrade base
	docker-compose exec backend alembic upgrade head

# Testing
test:
	docker-compose exec backend python -m pytest

# Health Check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health && echo "✅ Backend: OK" || echo "❌ Backend: Failed"
	@curl -f http://localhost:3000/health && echo "✅ Frontend: OK" || echo "❌ Frontend: Failed"

# Status
status:
	docker-compose ps

# Comprehensive Analysis Commands
comprehensive-build:
	@echo "Building comprehensive analysis system..."
	docker compose -f docker-compose.comprehensive.yml build --no-cache

comprehensive-up:
	@echo "Starting comprehensive analysis system..."
	docker compose -f docker-compose.comprehensive.yml up -d

comprehensive-down:
	@echo "Stopping comprehensive analysis system..."
	docker compose -f docker-compose.comprehensive.yml down

comprehensive-logs:
	docker compose -f docker-compose.comprehensive.yml logs -f

comprehensive-logs-backend:
	docker compose -f docker-compose.comprehensive.yml logs -f backend-comprehensive

comprehensive-logs-worker:
	docker compose -f docker-compose.comprehensive.yml logs -f analysis-worker

comprehensive-restart: comprehensive-down comprehensive-up
	@echo "Comprehensive analysis system restarted"

comprehensive-clean:
	@echo "Cleaning comprehensive analysis system..."
	docker compose -f docker-compose.comprehensive.yml down -v --remove-orphans

comprehensive-status:
	docker compose -f docker-compose.comprehensive.yml ps

comprehensive-health:
	@echo "Checking comprehensive analysis health..."
	@curl -f http://localhost:8001/health && echo "✅ Backend Comprehensive: OK" || echo "❌ Backend Comprehensive: Failed"
	@curl -f http://localhost:3001/health && echo "✅ Frontend Comprehensive: OK" || echo "❌ Frontend Comprehensive: Failed"

comprehensive-test:
	@echo "Testing comprehensive analysis API..."
	python3 test_comprehensive_api.py

comprehensive-demo:
	@echo "Running comprehensive analysis demo..."
	python3 demo_comprehensive_analysis.py

# Quick comprehensive analysis setup
comprehensive-quick: comprehensive-build comprehensive-up
	@echo "Comprehensive analysis system is starting..."
	@echo "Backend will be available at: http://localhost:8001"
	@echo "Frontend will be available at: http://localhost:3001"
	@echo "API docs will be available at: http://localhost:8001/docs"
	@echo "Monitoring dashboard at: http://localhost:8080"
	@echo ""
	@echo "Wait for services to start (about 2-3 minutes), then run:"
	@echo "  make comprehensive-test"
	@echo "  make comprehensive-demo"
