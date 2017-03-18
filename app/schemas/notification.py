from marshmallow import Schema, fields
from marshmallow import ValidationError
from marshmallow import validates
from marshmallow.validate import Length
from app import DB
from app import get_user_by_id


class NotificationSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    watcher_id = fields.Integer(default=None, missing=None)
    created = fields.DateTime(dump_only=True)
    received = fields.DateTime(default=None)
    message = fields.String(required=True, validate=Length(1, 100))

    @validates('user_id')
    def validate_user_id(self, value):
        if get_user_by_id(DB, value) is None:
            raise ValidationError('User with given ID does not exist')
