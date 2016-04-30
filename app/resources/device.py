from flask_restful import Resource, marshal
from app.db import DB
from app.db.channels import get_device_channels
from app.db.devices import get_all_devices, get_device
from app.resources import device_fields


class DeviceResource(Resource):
    def get(self, device_id=None):
        multiple = device_id is None

        if multiple:
            devices = get_all_devices(DB)
        else:
            devices = [get_device(DB, device_id)]

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
