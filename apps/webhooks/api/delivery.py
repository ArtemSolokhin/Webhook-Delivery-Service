from ninja import Router

from apps.webhooks.models import DeliveryAttempt
from apps.webhooks.schemas.delivery import DeliveryAttemptOut

router = Router()


@router.get(
    "/",
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
