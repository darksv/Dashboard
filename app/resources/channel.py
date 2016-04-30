from flask_restful import Resource, marshal
from app.db import DB
from app.db.channels import get_channel, get_all_channels
from app.resources import channel_fields


class ChannelResource(Resource):
    def get(self, channel_id=None):
        multiple = channel_id is None

        if multiple:
            channels = get_all_channels(DB)
        else:
            channels = [get_channel(DB, channel_id)]

        data = []

        for channel in channels:
            if channel is None:
                continue

            data.append(marshal(channel._asdict(), channel_fields))

        if len(data) == 0:
            return {}

        if not multiple:
            data = data[0]

        return dict(success=True, data=data, message=None)
