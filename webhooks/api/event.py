from django.db import transaction
from ninja import Router

from ..models import Event, WebhookEndpoint
from ..schemas.event import EventIn, EventOut
from ..tasks import deliver_webhook

router = Router()


@router.post(
    "/",
    response={201: EventOut, 200: EventOut},
    summary="Create an event and fan it out to active endpoints",
)
def create_event(request, payload: EventIn):
    event, created = Event.objects.get_or_create(
        event_id=payload.event_id,
        defaults={"event_type": payload.event_type, "payload": payload.payload},
    )
    # Not a real model field: attached only so the schema can report duplicates.
    event.duplicate = not created

    if not created:
        # Same event_id seen before: idempotent no-op, nothing re-delivered.
        return 200, event

    endpoint_ids = list(
        WebhookEndpoint.objects.filter(is_active=True).values_list("id", flat=True)
    )
    for endpoint_id in endpoint_ids:
        # Only enqueue once the Event row is actually committed, so the worker can find it.
        transaction.on_commit(
            lambda eid=endpoint_id, ev_id=event.event_id: deliver_webhook.delay(ev_id, eid)
        )

    return 201, event
