from typing import Optional, Union, List
from sqlalchemy import select, insert, func
from app.db import Database, DEVICES
from app.db.device import Device
from app.utils import extract_keys


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

    return Device(**extract_keys(row, ['id', 'uuid', 'name']))


def get_all_devices(db: Database) -> List[Device]:
    """
    Get all devices.
    """
    query = select(DEVICES.c).select_from(DEVICES)
    rows = db.execute(query)

    return [Device(**extract_keys(row, ['id', 'uuid', 'name'])) for row in rows]


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
