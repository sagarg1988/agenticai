# AgenticAI Platform

A production-ready scaffold for an AI Agent platform built with:
- **Django REST Framework** — API layer
- **LangGraph** — agent orchestration (plan → execute → synthesize loop)
- **Weaviate** — vector database for RAG / long-term memory
- **Redis + Celery** — async task queue
- **PostgreSQL** — relational persistence

---

## Quick Start (Local)

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- `gh` CLI (optional, for PR workflow)

### 1. Clone and configure environment

```bash
git clone https://github.com/sagarg1988/agenticai.git
cd agenticai

# Copy the sample env file and fill in secrets
cp .env.example .env   # TODO: create .env.example with all required vars
```

Required environment variables (set in `.env`):

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | Postgres connection string |
| `REDIS_URL` | Redis connection string |
| `WEAVIATE_URL` | Weaviate HTTP endpoint |
| `OPENAI_API_KEY` | OpenAI API key (or equivalent) |
| `DEBUG` | `True` for local dev |
| `ALLOWED_HOSTS` | Comma-separated hosts |

### 2. Start infrastructure

```bash
docker-compose up -d db redis weaviate
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Seed sample data (optional)

```bash
# TODO: add management command — python manage.py seed_data
```

### 5. Start the web server

```bash
python manage.py runserver
```

Or run everything via Docker Compose:

```bash
docker-compose up
```

### 6. Start Celery worker

```bash
celery -A aiagent worker -l info
```

### 7. Run tests

```bash
pytest
```

---

## Project Layout

```
agenticai/
├── aiagent/          # Django project package (settings, wsgi)
│   └── settings/
│       └── base.py
├── api/              # REST API (models, serializers, views, urls)
├── agents/           # Agent runner, planner, tool executor, synthesizer
├── tools/            # Tool registry and built-in tools
├── memory/           # Short-term and long-term (vector) memory
├── rag/              # Embedding provider and document ingestion
├── core/             # LLM provider abstraction
├── celery_tasks/     # Async Celery tasks
├── observability/    # Structured logging / tracing
├── deployments/      # Deployment-specific docker-compose overrides
└── tests/            # Pytest test suite
```

---

## Next Steps Checklist

- [ ] Run `python manage.py migrate` to apply initial migrations
- [ ] Seed sample data via management command
- [ ] `docker-compose up` to start all services
- [ ] Start Celery worker: `celery -A aiagent worker -l info`
- [ ] Run tests: `pytest`
- [ ] Configure secrets management (Vault / AWS Secrets Manager)
- [ ] Set up CI/CD pipeline
- [ ] Add production gunicorn configuration

---

## License

MIT — see [LICENSE](LICENSE)
