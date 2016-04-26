from app.db import DB
from app.db.channels import get_or_create_channel, update_channel
from flask import request
from flask_restful import Resource


class EntryResource(Resource):
    def put(self):
        args = request.get_json()

        channel_uuid = args.get('sensor_uuid', None)
        value = args.get('value', 0)

        channel = get_or_create_channel(DB, channel_uuid)

        if channel is not None:
            update_channel(DB, channel.id, value)

        return {}
