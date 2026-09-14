import json
from unittest import mock

from django.test import TestCase

from webhooks.models import Event, WebhookEndpoint


class IdempotencyTests(TestCase):
    """Re-submitting the same event_id must never create a duplicate Event or re-trigger deliveries."""

    def _post_event(self, event_id="evt-1"):
        return self.client.post(
            "/api/events/",
            data=json.dumps(
                {
                    "event_id": event_id,
                    "event_type": "order.created",
                    "payload": {"order_id": 42},
                }
            ),
            content_type="application/json",
        )

    @mock.patch("webhooks.api.event.deliver_webhook.delay")
    def test_duplicate_event_id_does_not_create_a_second_event(self, mock_delay):
        with self.captureOnCommitCallbacks(execute=True):
            first = self._post_event()
        with self.captureOnCommitCallbacks(execute=True):
            second = self._post_event()

        # 201 = created, 200 = same event_id seen before (idempotent no-op).
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(Event.objects.count(), 1)

    @mock.patch("webhooks.api.event.deliver_webhook.delay")
    def test_delivery_is_only_scheduled_on_first_submission(self, mock_delay):
        WebhookEndpoint.objects.create(url="http://example.com/hook-a", is_active=True)
        WebhookEndpoint.objects.create(url="http://example.com/hook-b", is_active=False)

        with self.captureOnCommitCallbacks(execute=True):
            self._post_event()
        with self.captureOnCommitCallbacks(execute=True):
            self._post_event()  # duplicate: must not schedule anything new

        # Exactly one active endpoint, exactly one submission counted.
        self.assertEqual(mock_delay.call_count, 1)
