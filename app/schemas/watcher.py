from marshmallow import Schema, fields


class WatcherSchema(Schema):
    id = fields.Integer()
    user_id = fields.Integer()
    channel_id = fields.Integer()
    condition = fields.String()
    message = fields.String()
    last_notification = fields.Boolean()
    renew_time = fields.Integer()
