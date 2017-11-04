from datetime import timedelta, datetime
from core import utils
from marshmallow import Schema, fields, decorators, ValidationError


class ApiChannelStatsSchema(Schema):
    _from = fields.Method(attribute='from', required=False, load_only=True, missing=None,
                          deserialize='parse_date', load_from='from')
    _to = fields.Method(attribute='to', required=False, load_only=True, missing=None,
                        deserialize='parse_date', load_from='to')
    _average = fields.Integer(attribute='average', required=False, load_only=True, missing=1,
                              load_from='average')

    @staticmethod
    def parse_date(value):
        try:
            return utils.parse_datetime(value)
        except ValueError:
            raise ValidationError('Invalid format.')

    @decorators.validates_schema(skip_on_field_errors=True)
    def validate_period_length(self, data):
        period_from = data['from']
        period_to = data['to']

        has_from = period_from is not None
        has_to = period_to is not None

        if has_from ^ has_to:
            invalid_field = 'from' if has_to else 'to'
            raise ValidationError('Only none or both period markers are supported.', [invalid_field])

        if not (has_from or has_to):
            return

        if (period_to - period_from).total_seconds() == 0:
            raise ValidationError('Period end must be later than start.', ['to'])

    @decorators.post_load
    def default_period(self, data):
        if data['to'] is None:
            now = datetime.now()
            data['to'] = now
            data['from'] = now - timedelta(minutes=60)
