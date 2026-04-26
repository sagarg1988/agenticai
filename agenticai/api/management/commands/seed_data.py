"""
Management command: seed_data

Populates the database with example AgentSessions, ConversationMessages,
LongTermMemory entries, and Documents so the API has ready-made data to
explore immediately after startup.

Run manually:
  python manage.py seed_data

It is idempotent — running it a second time is safe (it skips objects
that already carry the seeded marker in their metadata).
"""
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from api.models import AgentSession, ConversationMessage, Document, LongTermMemory

SEED_MARKER = {"seeded": True}


class Command(BaseCommand):
    help = "Seed the database with example data for development / testing"

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        user = User.objects.filter(username=username).first()
        if user is None:
            self.stdout.write(
                self.style.WARNING(
                    f"User '{username}' not found — run create_dev_superuser first."
                )
            )
            return

        # ---- Documents ------------------------------------------------
        docs = [
            {
                "title": "Agentic AI Overview",
                "source": "internal",
                "content": (
                    "Agentic AI systems are capable of planning, reasoning and "
                    "executing multi-step tasks autonomously. They combine large "
                    "language models with tool use, memory, and feedback loops."
                ),
            },
            {
                "title": "Vector Search Primer",
                "source": "internal",
                "content": (
                    "Vector search allows semantic retrieval by comparing dense "
                    "embedding vectors. Weaviate is an open-source vector database "
                    "that supports hybrid BM25 + vector queries."
                ),
            },
        ]
        for d in docs:
            obj, created = Document.objects.get_or_create(
                title=d["title"],
                defaults={
                    "source": d["source"],
                    "content": d["content"],
                    "metadata": SEED_MARKER,
                },
            )
            if created:
                self.stdout.write(f"  [+] Document: {d['title']}")

        # ---- Agent sessions + messages --------------------------------
        sessions_data = [
            {
                "messages": [
                    ("user", "What is agentic AI?"),
                    (
                        "assistant",
                        "Agentic AI refers to AI systems that autonomously plan "
                        "and execute complex multi-step tasks using tools and memory.",
                    ),
                ]
            },
            {
                "messages": [
                    ("user", "How does vector search work?"),
                    (
                        "assistant",
                        "Vector search converts text into dense embeddings and "
                        "retrieves semantically similar results using approximate "
                        "nearest-neighbor algorithms.",
                    ),
                    ("user", "Which vector databases exist?"),
                    (
                        "assistant",
                        "Popular options include Weaviate, Pinecone, Qdrant, "
                        "Chroma, and pgvector.",
                    ),
                ]
            },
        ]

        for session_data in sessions_data:
            # Use the first user message as a deduplication key stored in metadata
            first_msg = session_data["messages"][0][1]
            if AgentSession.objects.filter(
                metadata__seeded=True, metadata__first_msg=first_msg
            ).exists():
                continue

            session = AgentSession.objects.create(
                user=user,
                metadata={"seeded": True, "first_msg": first_msg},
            )
            for role, content in session_data["messages"]:
                ConversationMessage.objects.create(
                    session=session, role=role, content=content
                )
            self.stdout.write(
                f"  [+] Session {session.id} with {len(session_data['messages'])} messages"
            )

        # ---- Long-term memory entries ---------------------------------
        memories = [
            "User prefers concise explanations.",
            "User is interested in open-source vector databases.",
        ]
        for text in memories:
            obj, created = LongTermMemory.objects.get_or_create(
                text=text,
                defaults={"metadata": SEED_MARKER},
            )
            if created:
                self.stdout.write(f"  [+] Memory: {text[:60]}")

        self.stdout.write(self.style.SUCCESS("\nSeed data applied successfully."))
