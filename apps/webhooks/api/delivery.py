from ninja import Query, Router
from ninja.pagination import paginate

from apps.webhooks.models import DeliveryAttempt
from apps.webhooks.schemas.delivery import DeliveryAttemptOut, DeliveryFilters

router = Router()


@router.get(
    "/",
    response=list[DeliveryAttemptOut],
    summary="View delivery attempt history",
)
@paginate
def list_deliveries(request, filters: DeliveryFilters = Query(...)):
    qs = DeliveryAttempt.objects.select_related("event", "endpoint")
    return filters.filter(qs)
