from flask import request, jsonify, g
from api.schemas.channels_order import ChannelsOrderSchema
from core import DB
from core.services.channels import update_channels_order
from . import app, api_auth_required


@app.route('/api/order', methods=['POST'])
@api_auth_required
def api_update_order():
    data, errors = ChannelsOrderSchema().load(request.get_json() or request.args)
    if errors:
        return jsonify(errors=errors), 400
    with DB.connect() as db:
        update_channels_order(db, g.api_user.id, data['ids'])
    return jsonify()
