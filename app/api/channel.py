from datetime import timedelta, datetime
from flask import jsonify, request
from api import error, api_auth_required, internal_error, app
from api.schemas.channel import ChannelSchema
from api.schemas.watcher import WatcherSchema
from core import DB, utils
from core.services.channels import get_channel, update_channel, get_recent_channel_stats, get_channel_stats
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
