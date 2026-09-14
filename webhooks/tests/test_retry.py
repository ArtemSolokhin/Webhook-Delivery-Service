from unittest import mock

import requests
from django.test import TestCase, override_settings

from webhooks.enums import DeliveryStatus
from webhooks.models import DeliveryAttempt, Event, WebhookEndpoint
from webhooks.tasks import deliver_webhook


@override_settings(WEBHOOK_RETRY_DELAYS_SECONDS=[0, 0, 0])
class RetryBehaviorTests(TestCase):
    """apply() runs the task synchronously (including retries), so this needs no real Celery worker/broker."""

    def setUp(self):
        self.endpoint = WebhookEndpoint.objects.create(url="http://example.com/hook")
        self.event = Event.objects.create(event_id="evt-retry", event_type="order.created", payload={})

    @mock.patch("webhooks.services.requests.post")
    def test_retries_up_to_three_times_then_gives_up(self, mock_post):
        mock_post.side_effect = requests.ConnectionError("connection refused")

        deliver_webhook.apply(args=[self.event.event_id, self.endpoint.id])

        attempts = list(
            DeliveryAttempt.objects.filter(event=self.event, endpoint=self.endpoint).order_by("attempt_number")
        )
        # 1 initial attempt + 3 retries = 4 attempts total, all failed.
        self.assertEqual([a.attempt_number for a in attempts], [1, 2, 3, 4])
        self.assertTrue(all(a.status == DeliveryStatus.FAILED for a in attempts))
        self.assertEqual(mock_post.call_count, 4)

    @mock.patch("webhooks.services.requests.post")
    def test_succeeds_on_a_later_attempt_and_stops_retrying(self, mock_post):
        mock_post.side_effect = [
            requests.ConnectionError("connection refused"),
            mock.Mock(status_code=200, text="ok"),
        ]

        deliver_webhook.apply(args=[self.event.event_id, self.endpoint.id])

        attempts = list(
            DeliveryAttempt.objects.filter(event=self.event, endpoint=self.endpoint).order_by("attempt_number")
        )
        self.assertEqual([a.attempt_number for a in attempts], [1, 2])
        self.assertEqual(attempts[0].status, DeliveryStatus.FAILED)
        self.assertEqual(attempts[1].status, DeliveryStatus.SUCCESS)
        self.assertEqual(mock_post.call_count, 2)
