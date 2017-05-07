import re
from marshmallow import Schema, fields, ValidationError, validates
from marshmallow.validate import Length, OneOf
from app.channel_types import get_type_ids


class ChannelSchema(Schema):
    id = fields.Integer()
    uuid = fields.String()
    device_id = fields.Integer()
    name = fields.String(validate=Length(0, 100))
    type = fields.Integer(validate=OneOf(choices=get_type_ids()))
    value = fields.Float()
    value_updated = fields.DateTime()
    unit = fields.String(validate=Length(0, 10))
    color = fields.String()
    disabled = fields.Boolean()

    @validates('color')
    def validate_color(self, value):
        if not re.fullmatch(r'^#[0-9a-fA-F]{6}$', value):
            raise ValidationError('invalid color format')
