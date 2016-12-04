from binascii import hexlify
from datetime import datetime
from app.channel_types import get_type_by_id


class Channel:
    def __init__(self, id: int = None, uuid: bytes = None, device_id: int = None, type: int = None, name: str = None,
                 value: float = None, value_updated: datetime = None, unit: str = None):
        self._id = id
        self._uuid = uuid
        self._device_id = device_id
        self._type = type
        self._name = name
        self._value = value
        self._value_updated = value_updated
        self._unit = unit

    @property
    def id(self):
        return self._id

    @property
    def uuid(self):
        return hexlify(self._uuid).decode('ascii') if self._uuid is not None else None

    @property
    def device_id(self):
        return self._device_id

    @property
    def type(self):
        return get_type_by_id(self._type)

    @property
    def type_id(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def value_with_unit(self):
        if self.unit:
            return '{0} {1}'.format(self.value, self.unit)
        else:
            return str(self.value)

    @property
    def value_updated(self):
        return self._value_updated

    @property
    def unit(self):
        return (self._unit or '').strip()

    def save(self):
        pass