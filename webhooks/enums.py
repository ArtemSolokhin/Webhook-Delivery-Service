from django.db import models


class DeliveryStatus(models.TextChoices):
    """Outcome of one delivery attempt."""

    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
