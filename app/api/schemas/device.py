from marshmallow import Schema, fields
from marshmallow.validate import Length


class DeviceSchema(Schema):
    id = fields.Integer()
    uuid = fields.String()
    name = fields.String(validate=Length(0, 100))
