AI Agent scaffold (Django + LangGraph + Weaviate)

Quickstart (local dev)
1. Start infra:
   docker-compose up -d
2. Install dependencies:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
3. Run migrations:
   python manage.py migrate
4. Start dev server:
   python manage.py runserver 0.0.0.0:8000
5. Start a celery worker:
   celery -A aiagent worker -l info
6. Run tests:
   pytest

Local LLaMA 3 (Ollama)
1. Ensure Ollama is running and model exists:
   ollama pull llama3
2. Set environment variables:
   export LLM_PROVIDER=ollama
   export OLLAMA_BASE_URL=http://127.0.0.1:11434
   export OLLAMA_MODEL=llama3
3. Start the app as above (`runserver`, optional `celery`).

Notes:
- Configure environment variables (POSTGRES_*, OPENAI_API_KEY, WEAVIATE_URL) in .env for real usage.
- This scaffold is a starting point. See TODO comments in code for production hardening.
