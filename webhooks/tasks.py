from celery import shared_task
from django.conf import settings

from .models import Event, WebhookEndpoint
from .services import send_webhook


@shared_task(bind=True, max_retries=settings.WEBHOOK_MAX_RETRIES)
def deliver_webhook(self, event_id: str, endpoint_id: int) -> None:
    """Deliver one Event to one WebhookEndpoint, retrying on failure.

    attempt_number is derived from Celery's own retry counter, so it stays
    correct across the whole retry chain without any extra state:
    self.request.retries is 0 on the first run, 1 on the first retry, etc.
    """
    try:
        event = Event.objects.get(event_id=event_id)
        endpoint = WebhookEndpoint.objects.get(id=endpoint_id)
    except (Event.DoesNotExist, WebhookEndpoint.DoesNotExist):
        # Nothing sensible to retry - the event or endpoint is gone.
        return

    attempt_number = self.request.retries + 1
    attempt = send_webhook(endpoint, event, attempt_number)

    if attempt.status == attempt.Status.FAILED and self.request.retries < self.max_retries:
        delays = settings.WEBHOOK_RETRY_DELAYS_SECONDS
        countdown = delays[min(self.request.retries, len(delays) - 1)]
        raise self.retry(countdown=countdown)
