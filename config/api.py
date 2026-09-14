from ninja import NinjaAPI

from apps.webhooks.api.delivery import router as delivery_router
from apps.webhooks.api.endpoint import router as endpoint_router
from apps.webhooks.api.event import router as event_router

api = NinjaAPI(
    title="Webhook Delivery Service",
    version="1.0.0",
    urls_namespace="webhooks",
)

api.add_router("/endpoints/", endpoint_router)
api.add_router("/events/", event_router)
api.add_router("/deliveries/", delivery_router)
