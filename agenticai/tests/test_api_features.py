"""
Feature tests for the REST API.

These tests use Django's test client with an SQLite in-memory database
(no Postgres, Redis, or Weaviate required) to exercise:

  - POST /api/token/     — obtain an auth token
  - POST /api/query      — send a query to the agent (AgentRunner mocked)
  - Seeded data via the seed_data management command
  - Superuser creation via create_dev_superuser management command
"""
import json
import uuid
from unittest.mock import patch, MagicMock

import pytest
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api.models import AgentSession, ConversationMessage, Document, LongTermMemory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(username="testuser", password="testpass123"):
    user = User.objects.create_user(username=username, password=password)
    return user


def make_token(user):
    token, _ = Token.objects.get_or_create(user=user)
    return token.key


# ---------------------------------------------------------------------------
# Token endpoint tests
# ---------------------------------------------------------------------------

class TokenEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user()

    def test_obtain_token_valid_credentials(self):
        resp = self.client.post(
            "/api/token/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("token", resp.json())

    def test_obtain_token_invalid_password(self):
        resp = self.client.post(
            "/api/token/",
            {"username": "testuser", "password": "wrong"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_query_endpoint_requires_auth(self):
        resp = self.client.post("/api/query", {"input": "hello"}, format="json")
        self.assertEqual(resp.status_code, 401)


# ---------------------------------------------------------------------------
# Query endpoint tests
# ---------------------------------------------------------------------------

MOCK_RUNNER_RESULT = {
    "response": "Agentic AI is an AI system that can plan and act autonomously.",
    "sources": [],
    "plan_summary": "Direct LLM response",
}


class AgentQueryViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        token_key = make_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token_key}")

    @patch("api.views.AgentRunner")
    def test_query_creates_session_and_messages(self, MockRunner):
        MockRunner.return_value.run.return_value = MOCK_RUNNER_RESULT

        resp = self.client.post("/api/query", {"input": "What is agentic AI?"}, format="json")

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["response"], MOCK_RUNNER_RESULT["response"])

        # One session created
        self.assertEqual(AgentSession.objects.filter(user=self.user).count(), 1)
        session = AgentSession.objects.get(user=self.user)

        # User message + assistant message stored
        messages = list(session.messages.order_by("created_at"))
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].role, "user")
        self.assertEqual(messages[0].content, "What is agentic AI?")
        self.assertEqual(messages[1].role, "assistant")
        self.assertEqual(messages[1].content, MOCK_RUNNER_RESULT["response"])

    @patch("api.views.AgentRunner")
    def test_query_with_existing_session(self, MockRunner):
        MockRunner.return_value.run.return_value = MOCK_RUNNER_RESULT

        session = AgentSession.objects.create(user=self.user)
        resp = self.client.post(
            "/api/query",
            {"input": "Follow-up question", "session_id": str(session.id)},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        # Same session re-used (no new session created)
        self.assertEqual(AgentSession.objects.filter(user=self.user).count(), 1)

    def test_query_missing_input_returns_400(self):
        resp = self.client.post("/api/query", {}, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.json())

    def test_query_nonexistent_session_returns_404(self):
        resp = self.client.post(
            "/api/query",
            {"input": "hello", "session_id": str(uuid.uuid4())},
            format="json",
        )
        self.assertEqual(resp.status_code, 404)


# ---------------------------------------------------------------------------
# Management command: create_dev_superuser
# ---------------------------------------------------------------------------

class CreateDevSuperuserCommandTests(TestCase):
    def test_creates_superuser_and_token(self):
        from io import StringIO
        from django.core.management import call_command

        out = StringIO()
        call_command("create_dev_superuser", stdout=out)

        user = User.objects.get(username="admin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(Token.objects.filter(user=user).exists())
        output = out.getvalue()
        self.assertIn("admin", output)
        self.assertIn("Token", output)

    def test_idempotent_second_run(self):
        from io import StringIO
        from django.core.management import call_command

        call_command("create_dev_superuser", stdout=StringIO())
        # Running again must not raise
        out = StringIO()
        call_command("create_dev_superuser", stdout=out)
        self.assertIn("already exists", out.getvalue())
        self.assertEqual(User.objects.filter(username="admin").count(), 1)


# ---------------------------------------------------------------------------
# Management command: seed_data
# ---------------------------------------------------------------------------

class SeedDataCommandTests(TestCase):
    def _run_seed(self):
        from io import StringIO
        from django.core.management import call_command

        call_command("create_dev_superuser", stdout=StringIO())
        out = StringIO()
        call_command("seed_data", stdout=out)
        return out.getvalue()

    def test_seed_creates_documents(self):
        self._run_seed()
        self.assertGreaterEqual(Document.objects.count(), 2)

    def test_seed_creates_sessions_with_messages(self):
        self._run_seed()
        sessions = AgentSession.objects.filter(metadata__seeded=True)
        self.assertGreaterEqual(sessions.count(), 2)
        for s in sessions:
            self.assertGreater(s.messages.count(), 0)

    def test_seed_creates_long_term_memories(self):
        self._run_seed()
        self.assertGreaterEqual(LongTermMemory.objects.filter(metadata__seeded=True).count(), 2)

    def test_seed_is_idempotent(self):
        self._run_seed()
        doc_count = Document.objects.count()
        session_count = AgentSession.objects.count()
        # Second run
        self._run_seed()
        self.assertEqual(Document.objects.count(), doc_count)
        self.assertEqual(AgentSession.objects.count(), session_count)
