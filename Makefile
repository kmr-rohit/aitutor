.PHONY: backend frontend test up

backend:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -e .[dev] && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm install && npm run dev

test:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -e .[dev] && pytest

up:
	docker compose up --build
