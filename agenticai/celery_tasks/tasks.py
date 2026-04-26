from celery import shared_task
from rag.ingest import ingest_document

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def ingest_document_task(self, title, text, metadata):
    try:
        return ingest_document(title, text, metadata)
    except Exception as exc:
        raise self.retry(exc=exc)
