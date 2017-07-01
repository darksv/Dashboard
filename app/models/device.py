from binascii import hexlify
from app import DB
from app.db.channels import get_device_channels


class Device:
    def __init__(self, id: int = None, uuid: bytes = None, name: str = None):
        self._id = id
        self._uuid = uuid
        self._name = name

    @property
    def id(self):
        return self._id

    @property
    def uuid(self):
        return hexlify(self._uuid).decode('ascii') if self._uuid is not None else None

    @property
    def name(self):
        return self._name

    @property
    def channels(self):
        return get_device_channels(DB, self.id)
