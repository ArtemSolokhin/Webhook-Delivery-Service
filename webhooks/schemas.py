from datetime import datetime

from ninja import Schema
from pydantic import AnyHttpUrl


class EndpointIn(Schema):
    url: AnyHttpUrl
    is_active: bool = True


class EndpointOut(Schema):
    id: int
    url: str
    is_active: bool
    created_at: datetime


class EventIn(Schema):
    event_id: str
    event_type: str
    payload: dict = {}


class EventOut(Schema):
    id: int
    event_id: str
    event_type: str
    payload: dict
    created_at: datetime
    duplicate: bool = False


class DeliveryAttemptOut(Schema):
    id: int
    event_id: str
    event_type: str
    endpoint_id: int
    endpoint_url: str
    status: str
    http_status: int | None = None
    response_time: float | None = None
    attempt_number: int
    error_message: str
    created_at: datetime

    @staticmethod
    def resolve_event_id(obj):
        return obj.event.event_id

    @staticmethod
    def resolve_event_type(obj):
        return obj.event.event_type

    @staticmethod
    def resolve_endpoint_url(obj):
        return obj.endpoint.url
