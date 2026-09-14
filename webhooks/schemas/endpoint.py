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
