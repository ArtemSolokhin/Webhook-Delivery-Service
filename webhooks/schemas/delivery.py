from datetime import datetime

from ninja import Field, FilterSchema, Schema


class DeliveryFilters(FilterSchema):
    event_id: str | None = Field(None, json_schema_extra={"q": "event__event_id"})
    endpoint_id: int | None = None
    status: str | None = None


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
