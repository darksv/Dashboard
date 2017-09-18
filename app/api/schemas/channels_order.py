from marshmallow import Schema, fields


class ChannelsOrderSchema(Schema):
    ids = fields.List(fields.Integer(), load_only=True, required=True)
