from binascii import hexlify
from flask_restful import Resource, marshal, fields
from app.db import DB
from app.db.channels import get_device_channels
from app.db.devices import get_all_devices, get_device
from app.util import localize_datetime


class Bytes(fields.Raw):
    def format(self, value):
        return hexlify(value).decode('ascii')


class LocalizedDateTime(fields.Raw):
    def format(self, value):
        return localize_datetime(value).isoformat()


class DeviceResource(Resource):
    def get(self, device_id=None):
        multiple = device_id is None

        if multiple:
            devices = get_all_devices(DB)
        else:
            devices = [get_device(DB, device_id)]

        channel_fields = dict(
            id=fields.Integer,
            uuid=Bytes,
            device_id=fields.Integer,
            type=fields.Integer,
            name=fields.String,
            value=fields.Float,
            value_updated=LocalizedDateTime
        )

        device_fields = dict(
            id=fields.Integer,
            name=fields.String,
            uuid=Bytes,
            channels=fields.List(fields.Nested(channel_fields))
        )

        data = []

        for device in devices:
            device_data = device._asdict()
            device_data['channels'] = [c._asdict() for c in get_device_channels(DB, device_data['id'])]

            data.append(marshal(device_data, device_fields))

        if len(data) == 0:
            return {}

        if not multiple:
            data = data[0]

        return dict(success=True, data=data, message=None)
