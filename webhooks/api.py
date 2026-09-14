from django.db import transaction
from ninja import NinjaAPI

from .models import DeliveryAttempt, Event, WebhookEndpoint
from .schemas import DeliveryAttemptOut, EndpointIn, EndpointOut, EventIn, EventOut
from .tasks import deliver_webhook

api = NinjaAPI(
    title="Webhook Delivery Service",
    version="1.0.0",
    urls_namespace="webhooks",
)


# --- Webhook endpoints --------------------------------------------------

@api.post("/endpoints/", response={201: EndpointOut}, summary="Register a webhook endpoint")
def create_endpoint(request, payload: EndpointIn):
    endpoint = WebhookEndpoint.objects.create(
        url=str(payload.url), is_active=payload.is_active
    )
    return 201, endpoint


@api.get("/endpoints/", response=list[EndpointOut], summary="List registered endpoints")
def list_endpoints(request):
    return WebhookEndpoint.objects.all()


# --- Events ---------------------------------------------------------------

@api.post(
    "/events/",
    response={201: EventOut, 200: EventOut},
    summary="Create an event and fan it out to active endpoints",
)
def create_event(request, payload: EventIn):
    event, created = Event.objects.get_or_create(
        event_id=payload.event_id,
        defaults={"event_type": payload.event_type, "payload": payload.payload},
    )

    if not created:
        # Same event_id seen before: idempotent no-op, nothing re-delivered.
        return 200, EventOut(duplicate=True, **_event_dict(event))

    endpoint_ids = list(
        WebhookEndpoint.objects.filter(is_active=True).values_list("id", flat=True)
    )
    for endpoint_id in endpoint_ids:
        # Only enqueue once the Event row is actually committed, so the
        # worker is guaranteed to find it.
        transaction.on_commit(
            lambda eid=endpoint_id, ev_id=event.event_id: deliver_webhook.delay(ev_id, eid)
        )

    return 201, EventOut(duplicate=False, **_event_dict(event))


def _event_dict(event: Event) -> dict:
    return {
        "id": event.id,
        "event_id": event.event_id,
        "event_type": event.event_type,
        "payload": event.payload,
        "created_at": event.created_at,
    }


# --- Delivery history -------------------------------------------------

@api.get(
    "/deliveries/",
    response=list[DeliveryAttemptOut],
    summary="View delivery attempt history",
)
def list_deliveries(
    request,
    event_id: str | None = None,
    endpoint_id: int | None = None,
    status: str | None = None,
    limit: int = 50,
):
    qs = DeliveryAttempt.objects.select_related("event", "endpoint")
    if event_id:
        qs = qs.filter(event__event_id=event_id)
    if endpoint_id:
        qs = qs.filter(endpoint_id=endpoint_id)
    if status:
        qs = qs.filter(status=status)
    return qs[: max(1, min(limit, 200))]
