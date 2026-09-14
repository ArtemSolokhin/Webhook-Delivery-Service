from unittest import mock

from django.test import TestCase

from webhooks.enums import DeliveryStatus
from webhooks.models import DeliveryAttempt, Event, WebhookEndpoint
from webhooks.services import send_webhook


class SuccessfulDeliveryTests(TestCase):
    def setUp(self):
        self.endpoint = WebhookEndpoint.objects.create(url="http://example.com/hook")
        self.event = Event.objects.create(event_id="evt-success", event_type="order.created", payload={"order_id": 1})

    @mock.patch("webhooks.services.requests.post")
    def test_successful_delivery_is_recorded(self, mock_post):
        mock_post.return_value = mock.Mock(status_code=200, text="ok")

        attempt = send_webhook(self.endpoint, self.event, attempt_number=1)

        self.assertEqual(attempt.status, DeliveryStatus.SUCCESS)
        self.assertEqual(attempt.http_status, 200)
        self.assertEqual(attempt.attempt_number, 1)
        self.assertIsNotNone(attempt.response_time)
        self.assertGreaterEqual(attempt.response_time, 0)
        self.assertEqual(DeliveryAttempt.objects.count(), 1)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], self.endpoint.url)
        self.assertEqual(kwargs["json"]["event_id"], "evt-success")

    @mock.patch("webhooks.services.requests.post")
    def test_non_2xx_response_is_recorded_as_failed(self, mock_post):
        mock_post.return_value = mock.Mock(status_code=500, text="boom")

        attempt = send_webhook(self.endpoint, self.event, attempt_number=1)

        self.assertEqual(attempt.status, DeliveryStatus.FAILED)
        self.assertEqual(attempt.http_status, 500)
