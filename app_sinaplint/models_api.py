"""
API Key por utilizador (header ``X-API-Key``).
"""

from __future__ import annotations

import secrets

from django.conf import settings
from django.db import models


def _default_key() -> str:
    return f"sl_{secrets.token_urlsafe(32)}"


class APIKey(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sinaplint_api_keys",
    )
    name = models.CharField(max_length=80, blank=True, help_text="Rótulo opcional")
    key = models.CharField(max_length=64, unique=True, db_index=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "API Key SinapLint"
        verbose_name_plural = "API Keys SinapLint"
        ordering = ("-created_at",)

    def save(self, *args, **kwargs) -> None:
        if not self.key:
            self.key = _default_key()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user_id} ({self.key[:12]}…)"
