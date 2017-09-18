from flask import jsonify, g
from api import app, internal_error
from api.schemas.channel import ChannelSchema
from core import DB
from core.services.channels import get_all_channels_ordered, get_all_channels


@app.route('/api/channels', methods=['GET'])
def api_channels():
    with DB.connect() as db:
        channels = get_all_channels_ordered(db, g.api_user.id) if g.api_user else get_all_channels(db)
        data, errors = ChannelSchema().dump(channels, many=True)
        return jsonify(channels=data) if not errors else internal_error()
