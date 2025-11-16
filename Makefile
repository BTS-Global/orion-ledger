.PHONY: help install-backend install-frontend install dev-backend dev-frontend dev test-backend test-frontend test clean

help:
	@echo "Orion Ledger - Monorepo Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install              Install both backend and frontend dependencies"
	@echo "  make install-backend      Install backend dependencies"
	@echo "  make install-frontend     Install frontend dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev-backend          Run backend development server"
	@echo "  make dev-frontend         Run frontend development server"
	@echo "  make celery               Run Celery worker"
	@echo ""
	@echo "Testing:"
	@echo "  make test                 Run all tests"
	@echo "  make test-backend         Run backend tests"
	@echo "  make test-frontend        Run frontend tests"
	@echo ""
	@echo "Database:"
	@echo "  make migrate              Run Django migrations"
	@echo "  make makemigrations       Create new Django migrations"
	@echo "  make superuser            Create Django superuser"
	@echo ""
	@echo "Build:"
	@echo "  make build-frontend       Build frontend for production"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                Remove build artifacts and caches"

# Installation
install: install-backend install-frontend

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

# Development
dev-backend:
	cd backend && python manage.py runserver 8000

dev-frontend:
	cd frontend && npm run dev

celery:
	cd backend && celery -A backend worker -l info

# Database
migrate:
	cd backend && python manage.py migrate

makemigrations:
	cd backend && python manage.py makemigrations

superuser:
	cd backend && python manage.py createsuperuser

# Testing
test: test-backend test-frontend

test-backend:
	cd backend && python manage.py test

test-frontend:
	cd frontend && npm run test

# Build
build-frontend:
	cd frontend && npm run build

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/dist backend/build
	rm -rf frontend/dist frontend/node_modules/.vite
	@echo "Cleanup complete!"
