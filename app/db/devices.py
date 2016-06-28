from collections import namedtuple
from operator import attrgetter
from typing import Optional, Union, List
from sqlalchemy import select, insert, func
from app.db import Database, DEVICES

Device = namedtuple('Device', map(attrgetter('key'), DEVICES.c))


def get_device(db: Database, device_id: Union[int, str]) -> Optional[Device]:
    """
    Get device by ID or UUID.
    """
    if isinstance(device_id, int):
        condition = (DEVICES.c.id == device_id)
    elif isinstance(device_id, str):
        condition = (DEVICES.c.uuid == func.unhex(device_id))
    else:
        return None

    query = select(DEVICES.c).select_from(DEVICES).where(condition)
    result = db.execute(query)

    row = result.fetchone()

    if row is None:
        return None

    return Device(*row)


def get_all_devices(db: Database) -> List[Device]:
    """
    Get all devices.
    """

    query = select(DEVICES.c).select_from(DEVICES)
    result = db.execute(query)

    return [Device(*row) for row in result]


def create_device(db: Database, device_uuid: str, device_name: str='') -> Optional[Device]:
    """
    Create new device.
    """
    query = insert(DEVICES).values(
        uuid=func.unhex(device_uuid),
        name=device_name
    )
    result = db.execute(query)

    return get_device(db, device_id=result.lastrowid)


def get_or_create_device(db: Database, device_id: Union[int, str]) -> Optional[Device]:
    """
    Get device by ID or create.
    """
    device = get_device(db, device_id)
    if device is not None:
        return device

    device = create_device(db, device_id)
    if device is None:
        raise SystemError('Could not create device')

    return device
