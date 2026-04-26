FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY agenticai/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY agenticai/ /app/
CMD ["gunicorn", "aiagent.wsgi:application", "--bind", "0.0.0.0:8000"]
