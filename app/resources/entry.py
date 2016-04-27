from app.db import DB
from app.db.channels import get_or_create_channel, update_channel
from app.db.devices import get_or_create_device
from flask import request
from flask_restful import Resource


class EntryResource(Resource):
    def put(self):
        args = request.get_json()

        device_uuid = args.get('device_uuid', None)
        channel_uuid = args.get('sensor_uuid', None)
        value = args.get('value', 0)

        device = get_or_create_device(DB, device_uuid)
        if device is not None:
            channel = get_or_create_channel(DB, channel_uuid, device_id=device.id)

            if channel is not None:
                update_channel(DB, channel.id, value)

        return {}
