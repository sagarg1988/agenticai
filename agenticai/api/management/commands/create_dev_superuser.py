"""
Management command: create_dev_superuser

Creates a superuser and a DRF auth token for it, idempotently.
Credentials are read from environment variables so they are easy to
change in production without touching code.

  DJANGO_SUPERUSER_USERNAME  (default: admin)
  DJANGO_SUPERUSER_EMAIL     (default: admin@example.com)
  DJANGO_SUPERUSER_PASSWORD  (default: admin)
"""
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = "Create a dev superuser and print its API token (idempotent)"

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin")

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
        else:
            self.stdout.write(f"Superuser '{username}' already exists.")

        token, _ = Token.objects.get_or_create(user=user)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n--- Dev Credentials ---\n"
                f"  Username : {username}\n"
                f"  Password : (set via DJANGO_SUPERUSER_PASSWORD env var)\n"
                f"  API Token: {token.key}\n"
                f"\nObtain a token via:\n"
                f"  POST /api/token/  {{\"username\": \"{username}\", \"password\": \"<password>\"}}\n"
                f"\nUse the token in subsequent requests:\n"
                f"  Authorization: Token {token.key}\n"
            )
        )
