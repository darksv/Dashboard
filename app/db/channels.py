from collections import namedtuple
from datetime import datetime, timedelta
from operator import attrgetter
from typing import Optional, Union, List
from sqlalchemy import select, insert, update, func, and_
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
    result = db.execute(query)

    row = result.fetchone()

    if row is None:
        return None

    return Channel(*row)


def get_device_channels(db: Database, device_id: int) -> List[Channel]:
    """
    Get device channels.
    """
    query = select(CHANNELS.c).select_from(CHANNELS).where(CHANNELS.c.device_id == device_id)
    result = db.execute(query)

    return [Channel(*row) for row in result]


def get_all_channels(db: Database) -> List[Channel]:
    """
    Get all channels.
    """

    query = select(CHANNELS.c).select_from(CHANNELS)
    result = db.execute(query)

    return [Channel(*row) for row in result]


def create_channel(db: Database, device_id: int, channel_uuid: str, channel_type: int=0, channel_name: str='') -> Optional[Channel]:
    """
    Create new channel.
    """
    query = insert(CHANNELS).values(
        device_id=device_id,
        uuid=func.unhex(channel_uuid),
        type=channel_type,
        name=channel_name
    )
    result = db.execute(query)

    return get_channel(db, channel_id=result.lastrowid)


def get_or_create_channel(db: Database, channel_id: Union[int, str], device_id: int=None) -> Optional[Channel]:
    """
    Get channel by ID or create.
    """
    channel = get_channel(db, channel_id)
    if channel is not None:
        return channel

    channel = create_channel(db, device_id, channel_id)
    if channel is None:
        raise SystemError('Could not create a device')

    return channel


def update_channel_value(db: Database, channel_id: Union[int, str], value: float) -> bool:
    """
    Update channel value.
    """
    channel = get_channel(db, channel_id)
    if channel is None:
        return False

    now = datetime.now()

    if channel.value is not None and (channel.value_updated is None or channel.value_updated.minute != now.minute):
        # add entry to channel history
        query = insert(ENTRIES).values(
            channel_id=channel.id,
            value=channel.value,
            timestamp=channel.value_updated
        )

        db.execute(query)

    query = update(CHANNELS).values(
        value=value,
        value_updated=now
    ).where(CHANNELS.c.id == channel.id)

    db.execute(query)

    return True


def update_channel(db: Database, channel_id: int, channel_name: str = None, channel_type: int = None) -> bool:
    """
    Update channel name.
    """
    channel = get_channel(db, channel_id)
    if channel is None:
        return False

    values = dict()

    if channel_name is not None:
        values['name'] = channel_name

    if channel_type is not None:
        values['type'] = channel_type

    if len(values) > 0:
        query = update(CHANNELS).values(**values).where(CHANNELS.c.id == channel.id)

        db.execute(query)

    return True


def get_recent_channel_stats(db: Database, channel_id: int, count: int=100) -> List:
    """
    Get recent sensor's stats.
    """
    subquery = select([ENTRIES.c.timestamp, ENTRIES.c.value]) \
        .select_from(ENTRIES) \
        .where(ENTRIES.c.channel_id == channel_id) \
        .order_by(ENTRIES.c.timestamp.desc()) \
        .limit(count) \
        .alias()

    query = select(subquery.c) \
        .select_from(subquery) \
        .order_by(subquery.c.timestamp.asc()) \
        .limit(count)

    result = db.execute(query)

    return [(timestamp, value) for timestamp, value in result]


def get_daily_channel_stats(db: Database, channel_id: int, hours: int=24) -> List:
    """
    Get sensor's stats for last n hours.
    """
    query = select([func.hour(ENTRIES.c.timestamp), func.avg(ENTRIES.c.value)])\
        .select_from(ENTRIES)\
        .where(and_(ENTRIES.c.channel_id == channel_id, ENTRIES.c.timestamp >= datetime.now() - timedelta(hours=hours)))\
        .group_by(func.hour(ENTRIES.c.timestamp), func.date(ENTRIES.c.timestamp))\
        .order_by(ENTRIES.c.timestamp.asc())\
        .limit(hours)
    result = db.execute(query)

    return [['{0:02}:00'.format(hour), round(temp, 2)] for hour, temp in result]


def get_monthly_channel_stats(db: Database, channel_id: int, days: int=30) -> List:
    """
    Get sensor's stats for last n days.
    """
    query = select([func.date_format(ENTRIES.c.timestamp, '%e.%m'), func.avg(ENTRIES.c.value)])\
        .select_from(ENTRIES)\
        .where(and_(ENTRIES.c.channel_id == channel_id, ENTRIES.c.timestamp >= datetime.now() - timedelta(days=days)))\
        .group_by(func.day(ENTRIES.c.timestamp), func.date(ENTRIES.c.timestamp))\
        .order_by(ENTRIES.c.timestamp.asc())\
        .limit(days)
    result = db.execute(query)

    return [[day, round(temp, 2)] for day, temp in result]
