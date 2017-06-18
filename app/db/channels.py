from collections import OrderedDict
from datetime import datetime
from typing import Optional, Union, List
from sqlalchemy import select, delete, insert, update, func, and_, between
from sqlalchemy.exc import IntegrityError
from app.db import Database, CHANNELS, ENTRIES, CHANNELS_ORDER, USERS
from app.utils import extract_keys, minutes_between_dates, datetimes_between
from app.models.channel import Channel


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

    return Channel(**extract_keys(row, ['id', 'uuid', 'device_id', 'type', 'name', 'value', 'value_updated', 'unit', 'color', 'disabled']))


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


def get_all_channels_ordered(db: Database, user_id: int) -> List[Channel]:
    """
    Get all channels sorted by specified user's order.
    """
    joined = CHANNELS.outerjoin(CHANNELS_ORDER, CHANNELS_ORDER.c.channel_id == CHANNELS.c.id)\
        .join(USERS)

    query = select(CHANNELS.c)\
        .select_from(joined)\
        .where(USERS.c.id == user_id)\
        .order_by(CHANNELS_ORDER.c.order)
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


def update_channel_value(db: Database, channel_id: Union[int, str], value: float) -> None:
    """
    Update channel's value.
    """
    channel = get_channel(db, channel_id)
    if channel is None:
        return

    trans = db.conn.begin()
    try:
        now = datetime.now()

        if channel.value is not None and (channel.value_updated is None or channel.value_updated.minute != now.minute):
            query = insert(ENTRIES)\
                .values(
                    channel_id=channel.id,
                    value=channel.value,
                    timestamp=channel.value_updated)

            try:
                db.execute(query)
            except IntegrityError as e:
                # suppress duplication error
                pass

        query = update(CHANNELS)\
            .values(
                value=value,
                value_updated=now)\
            .where(CHANNELS.c.id == channel.id)
        db.execute(query)

        trans.commit()
    except:
        trans.rollback()
        raise


def update_channel(db: Database, channel_id: int, **values) -> bool:
    """
    Update channel's name.
    """
    channel = get_channel(db, channel_id)
    if channel is None:
        return False

    if len(values) > 0:
        query = update(CHANNELS).values(**values).where(CHANNELS.c.id == channel.id)

        db.execute(query)

    return True


def get_recent_channel_stats(db: Database, channel_id: int, period_start: datetime, period_end: datetime) -> List:
    """
    Get recent channels's stats.
    """
    query = select([ENTRIES.c.timestamp, ENTRIES.c.value]) \
        .select_from(ENTRIES) \
        .where(and_(ENTRIES.c.channel_id == channel_id,
                    between(ENTRIES.c.timestamp, period_start, period_end))) \
        .order_by(ENTRIES.c.timestamp.asc())

    result = db.execute(query)

    all_datetimes = OrderedDict.fromkeys(minutes_between_dates(period_start, period_end))
    for time, value in result:
        dt = time.replace(second=0)
        all_datetimes[dt] = round(value, 2)

    return [(time.strftime('%H:%M'), value) for time, value in all_datetimes.items()]


def get_channel_stats(db: Database, channel_id: int, period_start: datetime, period_end: datetime,
                      average_interval: int = 60) -> List:
    """
    Get channel's stats for specified period.
    """
    query = select([ENTRIES.c.timestamp, func.avg(ENTRIES.c.value)]) \
        .select_from(ENTRIES) \
        .where(and_(ENTRIES.c.channel_id == channel_id,
                    between(ENTRIES.c.timestamp, period_start, period_end))) \
        .group_by(func.date(ENTRIES.c.timestamp),
                  func.hour(ENTRIES.c.timestamp),
                  func.floor(func.minute(ENTRIES.c.timestamp) / average_interval)) \
        .order_by(ENTRIES.c.timestamp.asc())

    result = db.execute(query)

    all_datetimes = OrderedDict.fromkeys(datetimes_between(period_start, period_end, average_interval * 60))
    for time, value in result:
        dt = time.replace(minute=0, second=0)
        all_datetimes[dt] = round(value, 2)

    return [(time.strftime('%d.%m.%Y %H:00'), value) for time, value in all_datetimes.items()]


def update_channels_order(db: Database, user_id: int, channels: List[int]) -> None:
    """
    Update order of channels on dashboard for specified user.
    """
    trans = db.conn.begin()
    try:
        new_items = [dict(user_id=user_id, channel_id=channel_id, order=order)
                     for order, channel_id in enumerate(channels, 1)]

        query = delete(CHANNELS_ORDER).where(CHANNELS_ORDER.c.user_id == user_id)
        db.conn.execute(query)

        query = insert(CHANNELS_ORDER)
        db.conn.execute(query, new_items)

        trans.commit()
    except:
        trans.rollback()
        raise
