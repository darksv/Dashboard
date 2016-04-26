from collections import namedtuple
from datetime import datetime
from operator import attrgetter
from typing import Optional, Union
from sqlalchemy import select, insert, update, func
from app.db import Database, CHANNELS, ENTRIES

Channel = namedtuple('Channel', map(attrgetter('key'), CHANNELS.c))


def get_channel(db: Database, channel_id: Union[int, str]) -> Optional[Channel]:
    """
    Get channel by ID or UUID.
    """
    if isinstance(channel_id, int):
        condition = (CHANNELS.c.id == channel_id)
    elif isinstance(channel_id, str):
        condition = (CHANNELS.c.uuid == func.unhex(channel_id))
    else:
        return None

    query = select(CHANNELS.c).select_from(CHANNELS).where(condition)
    result = db.conn.execute(query)

    row = result.fetchone()

    if row is None:
        return None

    return Channel(*row)


def create_channel(db: Database, channel_uuid: str, channel_type: int=0, channel_name: str='') -> Optional[Channel]:
    """
    Create new channel.
    """
    query = insert(CHANNELS).values(
        device_id=1,
        uuid=func.unhex(channel_uuid),
        type=channel_type,
        name=channel_name
    )
    result = db.conn.execute(query)

    channel_id = result.lastrowid

    return get_channel(db, channel_id=channel_id)


def get_or_create_channel(db: Database, channel_id: Union[int, str]) -> Optional[Channel]:
    """
    Get channel by ID or create.
    """
    channel = get_channel(db, channel_id)
    if channel is not None:
        return channel

    return create_channel(db, channel_id)


def update_channel(db: Database, channel_id: Union[int, str], value: float) -> bool:
    """
    Update channel data.
    """
    channel = get_channel(db, channel_id)
    if channel is None:
        return False

    now = datetime.now()

    if channel.value_updated is None or channel.value_updated.minute != now.minute:
        # add entry to channel history
        query = insert(ENTRIES).values(
            channel_id=channel.id,
            value=value,
            timestamp=now
        )

        db.conn.execute(query)

    query = update(CHANNELS).values(
        value=value,
        value_updated=now
    ).where(CHANNELS.c.id == channel.id)

    db.conn.execute(query)

    return True
