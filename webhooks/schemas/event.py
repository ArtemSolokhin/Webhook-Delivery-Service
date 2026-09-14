from datetime import datetime

from ninja import Schema


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
