from typing import List
from sqlalchemy import select
from sqlalchemy.engine import Connection
from core.models import TRIGGERS
from core.models.trigger import Trigger
from core.utils import map_object


def get_triggers(db: Connection, channel_id: int) -> List[Trigger]:
    """
    Get triggers for given channel.
    """
    query = select(TRIGGERS.c, TRIGGERS.c.channel_id == channel_id)
    result = db.execute(query)

    return [map_object(Trigger, row) for row in result]
