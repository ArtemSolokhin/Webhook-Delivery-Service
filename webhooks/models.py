from django.db import models

from webhooks.enums import DeliveryStatus


class WebhookEndpoint(models.Model):
    """A subscriber URL that events are delivered to."""

    url = models.URLField(max_length=2000)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.url


class Event(models.Model):
    """An event to fan out to active endpoints; event_id is the idempotency key."""

    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=255)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} ({self.event_id})"


class DeliveryAttempt(models.Model):
    """The result of one attempt to deliver an Event to a WebhookEndpoint."""

    event = models.ForeignKey(Event, related_name="delivery_attempts", on_delete=models.CASCADE)
    endpoint = models.ForeignKey(WebhookEndpoint, related_name="delivery_attempts", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=DeliveryStatus.choices)
    http_status = models.PositiveSmallIntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True, help_text="Seconds elapsed waiting for a response.")
    attempt_number = models.PositiveSmallIntegerField()
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["event", "endpoint"])]

    def __str__(self):
        return f"attempt #{self.attempt_number} for event {self.event_id} -> {self.endpoint_id} [{self.status}]"
