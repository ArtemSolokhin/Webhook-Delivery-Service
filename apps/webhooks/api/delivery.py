from ninja import Query, Router

from apps.webhooks.models import DeliveryAttempt
from apps.webhooks.schemas.delivery import DeliveryAttemptOut, DeliveryFilters

router = Router()


@router.get(
    "/",
    response=list[DeliveryAttemptOut],
    summary="View delivery attempt history",
)
def list_deliveries(request, filters: DeliveryFilters = Query(...), limit: int = 50):
    qs = DeliveryAttempt.objects.select_related("event", "endpoint")
    qs = filters.filter(qs)
    return qs[: max(1, min(limit, 200))]
