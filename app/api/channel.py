from flask import jsonify, request
from api import error, api_auth_required, internal_error, app
from api.schemas.channel import ChannelSchema
from api.schemas.requests import ApiChannelStatsSchema
from api.schemas.trigger import TriggerSchema
from core import DB
from core.services.channels import get_channel, update_channel, get_channel_stats
from core.services.triggers import get_triggers


@app.route('/api/channel/<int:channel_id>/stats')
def api_channel_stats(channel_id: int):
    with DB.connect() as db:
        channel = get_channel(db, channel_id)
        if not channel:
            return error('Resource not found', 404)

        options, errors = ApiChannelStatsSchema().load(request.args)
        if errors:
            return jsonify(errors=errors), 400

        history_from = options['from']
        history_to = options['to']
        history_averaging = options['average']

        items = get_channel_stats(db, channel_id, history_from, history_to, history_averaging)
        label_format = '%H:%M' if history_averaging == 1 else '%d.%m.%Y %H:00'
        items = ((time.strftime(label_format), round(value, 2) if value else None) for time, value in items)

        title = channel.name
        unit = channel.unit
        labels, values = zip(*items)

        return jsonify(title=title, unit=unit, labels=labels, values=values)


@app.route('/api/channel/<int:channel_id>/triggers', methods=['GET'])
def api_channel_triggers(channel_id: int):
    with DB.connect() as db:
        triggers = get_triggers(db, channel_id)
        data, errors = TriggerSchema().dump(triggers, many=True)
        return jsonify(triggers=data) if not errors else internal_error()


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
