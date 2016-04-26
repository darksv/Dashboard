from datetime import datetime, timedelta
from typing import List
from sqlalchemy import select, func, and_
from app.db import Database, ENTRIES


def get_daily_stats(db: Database, sensor_id: int, hours: int=24) -> List:
    """
    Get sensor's stats for last n hours.
    """
    query = select([func.hour(ENTRIES.c.timestamp), func.avg(ENTRIES.c.value)])\
        .select_from(ENTRIES)\
        .where(and_(ENTRIES.c.sensor_id == sensor_id, ENTRIES.c.timestamp >= datetime.now() - timedelta(hours=hours)))\
        .group_by(func.hour(ENTRIES.c.timestamp), func.date(ENTRIES.c.timestamp))\
        .order_by(ENTRIES.c.timestamp.asc())\
        .limit(hours)
    result = db.conn.execute(query)

    return [['{0:02}:00'.format(hour), round(temp, 2)] for hour, temp in result]


def get_monthly_stats(db: Database, sensor_id: int, days: int=30) -> List:
    """
    Get sensor's stats for last n days.
    """
    query = select([func.date_format(ENTRIES.c.timestamp, '%e.%m'), func.avg(ENTRIES.c.value)])\
        .select_from(ENTRIES)\
        .where(and_(ENTRIES.c.sensor_id == sensor_id, ENTRIES.c.timestamp >= datetime.now() - timedelta(days=days)))\
        .group_by(func.day(ENTRIES.c.timestamp), func.date(ENTRIES.c.timestamp))\
        .order_by(ENTRIES.c.timestamp.asc())\
        .limit(days)
    result = db.conn.execute(query)

    return [[day, round(temp, 2)] for day, temp in result]
