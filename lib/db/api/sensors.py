from collections import namedtuple
from operator import attrgetter
from typing import Optional, List
from sqlalchemy import select, insert
from lib.db import Database, SENSORS

Sensor = namedtuple('Sensor', map(attrgetter('key'), SENSORS.c))


def get_all_sensors(db: Database) -> List[Sensor]:
    """
    Get all sensors.
    """
    query = select(SENSORS.c).select_from(SENSORS)
    result = db.conn.execute(query)

    return [Sensor(*row) for row in result]


def get_sensor_by_internal_id(db: Database, internal_id: str) -> Optional[Sensor]:
    """
    Get sensor by its internal ID.
    """
    query = select(SENSORS.c).select_from(SENSORS).where(SENSORS.c.internal_id == internal_id)
    result = db.conn.execute(query)

    row = result.fetchone()

    if row is None:
        return None

    return Sensor(*row)


def get_sensor(db: Database, sensor_id: int) -> Optional[Sensor]:
    """
    Get sensor by its ID.
    """
    query = select(SENSORS.c).select_from(SENSORS).where(SENSORS.c.id == sensor_id)
    result = db.conn.execute(query)

    row = result.fetchone()

    if row is None:
        return None

    return Sensor(*row)


def create_sensor(db: Database, internal_id: str, sensor_type: int, title: str=None) -> Optional[Sensor]:
    """
    Create new sensor.
    """
    query = insert(SENSORS).values(internal_id=internal_id, type=sensor_type, title=title)
    result = db.conn.execute(query)

    sensor_id = result.lastrowid

    return get_sensor(db, sensor_id)
