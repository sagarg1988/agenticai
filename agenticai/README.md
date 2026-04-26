AI Agent scaffold (Django + LangGraph + Weaviate)

## Start everything with one command

```
docker-compose up --build
```

This starts all modules in one go:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Weaviate vector store (port 8080)
- Django web server (port 8000) — migrations run automatically
- Celery worker

## Local development (without Docker)

1. Start infrastructure services only:
   ```
   docker-compose up -d db redis weaviate
   ```
2. Install dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```
   python manage.py migrate
   ```
4. Start the dev server:
   ```
   python manage.py runserver 0.0.0.0:8000
   ```
5. Start a Celery worker (separate terminal):
   ```
   celery -A aiagent worker -l info
   ```
6. Run tests:
   ```
   pytest
   ```

## Local LLaMA 3 (Ollama)

1. Ensure Ollama is running and the model is pulled:
   ```
   ollama pull llama3
   ```
2. Set environment variables:
   ```
   export LLM_PROVIDER=ollama
   export OLLAMA_BASE_URL=http://127.0.0.1:11434
   export OLLAMA_MODEL=llama3
   ```
3. Start the app as above (`runserver`, optional `celery`).

## Notes

- Copy `.env.example` to `.env` and set `POSTGRES_*`, `OPENAI_API_KEY`, `WEAVIATE_URL` for real usage.
- This scaffold is a starting point. See TODO comments in code for production hardening.
