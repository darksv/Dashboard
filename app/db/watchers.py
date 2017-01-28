from typing import List
from sqlalchemy import select
from app.db import Database, WATCHERS
from app.models.watcher import Watcher


def get_watchers(db: Database, channel_id: int) -> List[Watcher]:
    """
    Get monitors for given channel.
    """
    query = select(WATCHERS.c, WATCHERS.c.channel_id == channel_id)
    result = db.execute(query)

    return [Watcher(*row) for row in result]
