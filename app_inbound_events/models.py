import uuid
from django.db import models
from django.utils import timezone


class InboundEventStatus(models.TextChoices):
    RECEIVED = "RECEIVED", "Received"
    ENQUEUED = "ENQUEUED", "Enqueued"
    PROCESSING = "PROCESSING", "Processing"
    PROCESSED = "PROCESSED", "Processed"
    FAILED = "FAILED", "Failed"


class InboundEvent(models.Model):
    """
    Event sourcing leve: guarda o evento bruto + status.
    Idempotência é garantida por event_id único + lock Redis nas tasks.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.CharField(max_length=128, unique=True, db_index=True)
    source = models.CharField(max_length=64, db_index=True)
    payload_json = models.JSONField(default=dict, blank=True)

    received_at = models.DateTimeField(default=timezone.now, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=24,
        choices=InboundEventStatus.choices,
        default=InboundEventStatus.RECEIVED,
        db_index=True,
    )
    error_message = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-received_at"]

    def __str__(self) -> str:
        return f"InboundEvent(event_id={self.event_id}, source={self.source}, status={self.status})"
