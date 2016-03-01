from collections import namedtuple
from datetime import datetime
from operator import attrgetter
from typing import Optional
from sqlalchemy import select, insert
from app.db import Database, READINGS

Reading = namedtuple('Reading', map(attrgetter('key'), READINGS.c))


def get_reading(db: Database, reading_id: int) -> Optional[Reading]:
    """
    Get reading by its ID.
    """
    query = select(READINGS.c).select_from(READINGS).where(READINGS.c.id == reading_id)
    result = db.conn.execute(query)

    row = result.fetchone()

    if row is None:
        return None

    return Reading(*row)


def get_last_reading(db: Database, sensor_id: int) -> Optional[Reading]:
    """
    Get last sensor's reading.
    """
    query = select(READINGS.c).select_from(READINGS)\
        .where(READINGS.c.sensor_id == sensor_id)\
        .order_by(READINGS.c.timestamp.desc())\
        .limit(1)
    result = db.conn.execute(query)

    row = result.fetchone()

    if row is None:
        return None

    return Reading(*row)


def create_reading(db: Database, sensor_id: int, value: float) -> Optional[Reading]:
    """
    Create new reading.
    """
    query = insert(READINGS).values(sensor_id=sensor_id, value=value, timestamp=datetime.now())
    result = db.conn.execute(query)

    sensor_id = result.lastrowid

    return get_reading(db, sensor_id)
