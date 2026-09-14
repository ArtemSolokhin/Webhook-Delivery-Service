"""Delivery logic: send one HTTP request for one attempt and record it. Kept separate from the Celery task so it can be unit tested directly."""
import time

import requests
from django.conf import settings

from .models import DeliveryAttempt, Event, WebhookEndpoint


def send_webhook(endpoint: WebhookEndpoint, event: Event, attempt_number: int) -> DeliveryAttempt:
    """POST the event once and record the result; never raises, failures are recorded as a failed attempt."""
    body = {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "payload": event.payload,
    }

    started_at = time.monotonic()
    try:
        response = requests.post(
            endpoint.url,
            json=body,
            timeout=settings.WEBHOOK_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        elapsed = time.monotonic() - started_at
        return DeliveryAttempt.objects.create(
            event=event,
            endpoint=endpoint,
            status=DeliveryAttempt.Status.FAILED,
            http_status=None,
            response_time=elapsed,
            attempt_number=attempt_number,
            error_message=str(exc)[:2000],
        )

    elapsed = time.monotonic() - started_at
    success = 200 <= response.status_code < 300
    return DeliveryAttempt.objects.create(
        event=event,
        endpoint=endpoint,
        status=DeliveryAttempt.Status.SUCCESS if success else DeliveryAttempt.Status.FAILED,
        http_status=response.status_code,
        response_time=elapsed,
        attempt_number=attempt_number,
        error_message="" if success else response.text[:2000],
    )
