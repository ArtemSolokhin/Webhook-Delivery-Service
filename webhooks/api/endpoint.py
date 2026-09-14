from ninja import Router

from ..models import WebhookEndpoint
from ..schemas.endpoint import EndpointIn, EndpointOut

router = Router()


@router.post("/", response={201: EndpointOut}, summary="Register a webhook endpoint")
def create_endpoint(request, payload: EndpointIn):
    endpoint = WebhookEndpoint.objects.create(
        url=str(payload.url), is_active=payload.is_active
    )
    return 201, endpoint


@router.get("/", response=list[EndpointOut], summary="List registered endpoints")
def list_endpoints(request):
    return WebhookEndpoint.objects.all()
