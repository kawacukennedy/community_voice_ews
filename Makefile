.PHONY: install dev dev-backend dev-frontend test lint format seed clean \
        docker-up docker-down deploy deploy-backend

install:
	cd backend && pip install -r requirements.txt

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	python3 -m http.server 5500 -d frontend

dev:
	@echo "Starting backend on :8000 and frontend on :5500"
	@echo "Open http://localhost:5500 in your browser"
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	python3 -m http.server 5500 -d frontend

test:
	cd backend && python -m pytest tests/ -v

test-coverage:
	cd backend && python -m pytest tests/ -v --cov=app

lint:
	cd backend && flake8 app/ --max-line-length=120 --extend-ignore=E203 --count
	cd backend && black --check app/ --line-length=120

format:
	cd backend && black app/ --line-length=120

seed:
	python scripts/seed_data.py

seed-local:
	python scripts/seed_data.py http://localhost:8000

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

deploy:
	git push origin main
	@echo "CI/CD will deploy automatically"

deploy-backend: deploy
