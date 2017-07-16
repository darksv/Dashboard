from marshmallow import Schema, fields


class UserSchema(Schema):
    name = fields.String()
    hash = fields.String()
    is_authenticated = fields.Boolean()
