from binascii import hexlify
from app.db import DB
from app.db.channels import get_channel, get_all_channels
from app.util import localize_datetime
from flask_restful import Resource


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

            channel_data = channel._asdict()
            channel_data['uuid'] = hexlify(channel_data['uuid']).decode('ascii')
            channel_data['value_updated'] = localize_datetime(channel_data['value_updated']).isoformat()

            data.append(channel_data)

        if len(data) == 0:
            return {}

        if not multiple:
            data = data[0]

        return dict(success=True, data=data, message=None)
