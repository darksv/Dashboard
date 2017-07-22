from collections import defaultdict
from datetime import timedelta, datetime
from flask import jsonify, request
import config
from api import error, api_auth_required, internal_error, app
from api.schemas.channel import ChannelSchema
from api.schemas.watcher import WatcherSchema
from core import DB, utils
from core.models.channel_type import ChannelType
from core.services.channel_update import AverageCalculator
from core.services.channels import get_channel, get_or_create_channel, update_channel, get_recent_channel_stats, \
    get_channel_stats, log_channel_value
from core.services.devices import get_or_create_device
from core.services.watchers import get_watchers


@app.route('/api/channel/<int:channel_id>/stats')
def api_channel_stats(channel_id: int):
    with DB.connect() as db:
        channel = get_channel(db, channel_id)
        if not channel:
            return jsonify()

        labels = []
        values = []

        period = request.args.get('type', 'recent')
        if period == 'recent':
            period_end = datetime.now()
            period_start = period_end - timedelta(minutes=60)

            labels, values = zip(*get_recent_channel_stats(db, channel_id, period_start, period_end))
        elif period == 'custom':
            try:
                period_start = utils.parse_datetime(request.args.get('from'))
                period_end = utils.parse_datetime(request.args.get('to'))
            except ValueError:
                return error('Bad request', 400)
            else:
                if (period_end - period_start).total_seconds() > 0:
                    labels, values = zip(*get_channel_stats(db, channel_id, period_start, period_end))

        title = channel.name
        unit = channel.unit

        return jsonify(title=title, unit=unit, labels=labels, values=values)


@app.route('/api/channel/<int:channel_id>/watchers', methods=['GET'])
def api_channel_watchers(channel_id: int):
    with DB.connect() as db:
        watchers = get_watchers(db, channel_id)
        data, errors = WatcherSchema().dump(watchers, many=True)
        return jsonify(watchers=data) if not errors else internal_error()


@app.route('/api/channel/<int:channel_id>', methods=['GET'])
def api_channel_settings(channel_id: int):
    with DB.connect() as db:
        channel = get_channel(db, channel_id)
        if not channel:
            return error('Channel not found')

        data, errors = ChannelSchema().dump(channel)
        return jsonify(data) if not errors else internal_error()


@app.route('/api/channel/<int:channel_id>', methods=['POST'])
@api_auth_required
def api_channel_update(channel_id: int):
    with DB.connect() as db:
        channel = get_channel(db, channel_id)
        if not channel:
            return jsonify(), 404

        data, errors = ChannelSchema().load(request.get_json() or request.args)
        if errors:
            return jsonify(errors=errors), 400

        if update_channel(db, channel_id, **data):
            return jsonify()

        return jsonify(), 500


calculators = defaultdict(lambda: AverageCalculator(
    period=config.MEASUREMENT_AVERAGING_PERIOD,
    start_at=datetime.now().replace(second=0, microsecond=0)
))


@app.route('/channelUpdate', methods=['POST'])
def channel_update():
    with DB.connect() as db:
        device_uuid = request.form.get('device_uuid')
        channel_uuid = request.form.get('channel_uuid')
        raw_value = request.form.get('value')

        device = get_or_create_device(db, device_uuid)
        channel = get_or_create_channel(db, channel_uuid, device_id=device.id)

        if channel.type is ChannelType.FLOATING:
            value = float(raw_value)

            update_channel(db, channel.id, value=value, value_updated=datetime.now())

            calculator = calculators[channel.id]
            calculator.push_value(value)
            if calculator.has_average:
                value, timestamp = calculator.pop_average()
                log_channel_value(db, channel.id, value, timestamp, ignore_duplicates=True)

                return jsonify(
                    channel_id=channel.id,
                    value=value,
                    timestamp=timestamp.isoformat()
                )

        return jsonify(channel_id=channel.id)
