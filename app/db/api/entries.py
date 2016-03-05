from collections import namedtuple
from datetime import datetime
from operator import attrgetter
from typing import Optional
from sqlalchemy import select, insert
from app.db import Database, ENTRIES

Entry = namedtuple('Entry', map(attrgetter('key'), ENTRIES.c))


def get_entry(db: Database, entry_id: int) -> Optional[Entry]:
    """
    Get entry by its ID.
    """
    query = select(ENTRIES.c).select_from(ENTRIES).where(ENTRIES.c.id == entry_id)
    result = db.conn.execute(query)

    row = result.fetchone()

    if row is None:
        return None

    return Entry(*row)


def get_last_entry(db: Database, sensor_id: int) -> Optional[Entry]:
    """
    Get last sensor's entry.
    """
    query = select(ENTRIES.c).select_from(ENTRIES)\
        .where(ENTRIES.c.sensor_id == sensor_id)\
        .order_by(ENTRIES.c.timestamp.desc())\
        .limit(1)
    result = db.conn.execute(query)

    row = result.fetchone()

    if row is None:
        return None

    return Entry(*row)


def create_entry(db: Database, sensor_id: int, value: float) -> Optional[Entry]:
    """
    Create new entry.
    """
    query = insert(ENTRIES).values(sensor_id=sensor_id, value=value, timestamp=datetime.now())
    result = db.conn.execute(query)

    sensor_id = result.lastrowid

    return get_entry(db, sensor_id)
