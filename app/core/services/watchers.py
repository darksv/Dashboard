from typing import List
from sqlalchemy import select
from sqlalchemy.engine import Connection
from core.models import WATCHERS
from core.models.watcher import Watcher
from core.utils import map_object


def get_watchers(db: Connection, channel_id: int) -> List[Watcher]:
    """
    Get monitors for given channel.
    """
    query = select(WATCHERS.c, WATCHERS.c.channel_id == channel_id)
    result = db.execute(query)

    return [map_object(Watcher, row) for row in result]
