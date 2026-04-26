# AgenticAI Platform

A production-ready scaffold for an AI Agent platform built with **Django**, **LangGraph**, and **Weaviate**.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | Django 4.2 + Django REST Framework |
| Agent orchestration | LangGraph + LangChain |
| Vector store | Weaviate |
| Task queue | Celery + Redis |
| Database | PostgreSQL |
| Observability | structlog |

---

## Running Locally

### Prerequisites
- Docker & Docker Compose
- Python 3.11+

### 1. Clone & configure environment

```bash
git clone https://github.com/sagarg1988/agenticai.git
cd agenticai
cp .env.example .env   # edit .env with your secrets (OPENAI_API_KEY, etc.)
```

### 2. Start all services

```bash
docker-compose up --build
```

This starts PostgreSQL, Redis, Weaviate, the Django web server, and a Celery worker.

### 3. Run migrations

```bash
docker-compose exec web python manage.py migrate
```

### 4. Seed sample data (optional)

```bash
docker-compose exec web python manage.py loaddata agenticai/fixtures/sample.json
```

### 5. Start Celery worker (standalone)

```bash
celery -A agenticai.celery_tasks worker --loglevel=info
```

### 6. Run tests

```bash
pytest agenticai/tests/
```

### 7. API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/agents/` | List agents |
| POST | `/api/agents/` | Create agent |
| POST | `/api/agents/{id}/run/` | Run agent |

---

## Next Steps Checklist

- [ ] Run migrations: `python manage.py migrate`
- [ ] Seed sample data: `python manage.py loaddata agenticai/fixtures/sample.json`
- [ ] Run docker-compose: `docker-compose up --build`
- [ ] Start celery worker: `celery -A agenticai.celery_tasks worker --loglevel=info`
- [ ] Run tests: `pytest agenticai/tests/`
- [ ] Set production secrets in `.env` (OPENAI_API_KEY, SECRET_KEY, DATABASE_URL)
- [ ] Configure Weaviate schema & ingest documents via `agenticai/rag/ingest.py`
- [ ] Enable sandbox for `python_fn` tool (Docker-in-Docker or gVisor)
- [ ] Add authentication (e.g., JWT) to API endpoints
- [ ] Set up CI/CD pipeline
