from binascii import hexlify
from flask_restful import fields
from app.util import localize_datetime


class HexlifiedBytes(fields.Raw):
    def format(self, value):
        return hexlify(value).decode('ascii')


class ISO8601Datetime(fields.Raw):
    def format(self, value, localized=True):
        if localized:
            value = localize_datetime(value)

        return value.isoformat()

channel_fields = dict(
    id=fields.Integer,
    uuid=HexlifiedBytes,
    device_id=fields.Integer,
    type=fields.Integer,
    name=fields.String,
    value=fields.Float,
    value_updated=ISO8601Datetime
)

device_fields = dict(
    id=fields.Integer,
    name=fields.String,
    uuid=HexlifiedBytes,
    channels=fields.List(fields.Nested(channel_fields))
)
