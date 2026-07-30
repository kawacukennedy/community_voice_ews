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
	cd backend && python -c "
	import requests, json
	base = 'http://localhost:8000'
	communities = [
		{'name': 'Kibera Community', 'phone': '+254712345678', 'region': 'Nairobi', 'country': 'Kenya', 'latitude': -1.315, 'longitude': 36.785},
		{'name': 'Kampala North', 'phone': '+256712345678', 'region': 'Kampala', 'country': 'Uganda', 'latitude': 0.347, 'longitude': 32.582},
		{'name': 'Mogadishu Central', 'phone': '+252612345678', 'region': 'Mogadishu', 'country': 'Somalia', 'latitude': 2.046, 'longitude': 45.318},
	]
	for c in communities:
		r = requests.post(f'{base}/api/communities', json=c)
		print(f'Created: {c[\"name\"]} - {r.status_code}')
	reports = [
		{'message': 'Heavy flooding in the village near the river, water entering homes', 'latitude': -1.315, 'longitude': 36.785, 'location_name': 'Nairobi River Basin', 'source': 'demo'},
		{'message': 'No rain for months, crops failing, livestock dying from thirst', 'latitude': 0.347, 'longitude': 32.582, 'location_name': 'Kampala Region', 'source': 'demo'},
		{'message': 'Desert locust swarm spotted moving east across farms', 'latitude': 2.046, 'longitude': 45.318, 'location_name': 'Mogadishu Area', 'source': 'demo'},
	]
	for r in reports:
		resp = requests.post(f'{base}/api/reports', json=r)
		print(f'Report created: {resp.status_code}')
	print('Seed complete!')
	"

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
