import re
from marshmallow import Schema, fields, ValidationError, validates
from marshmallow.validate import Length
from app.channel_type import ChannelType


class ChannelSchema(Schema):
    id = fields.Integer(dump_only=True)
    uuid = fields.String(dump_only=True)
    device_id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(0, 100))
    type = fields.Function(lambda obj: obj.type.value, lambda value: ChannelType(value))
    value = fields.Float(dump_only=True)
    value_updated = fields.DateTime(dump_only=True)
    unit = fields.String(validate=Length(0, 10))
    color = fields.String()
    disabled = fields.Boolean()

    @validates('color')
    def validate_color(self, value):
        if not re.fullmatch(r'^#[0-9a-fA-F]{6}$', value):
            raise ValidationError('invalid color format')

    @validates('type')
    def validate_type(self, value):
        if value not in ChannelType:
            raise ValidationError('unknown channel function')
