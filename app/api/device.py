from flask import jsonify
from api import internal_error, error, app
from api.schemas.device import DeviceSchema
from core import DB
from core.services.devices import get_device


@app.route('/api/device/<int:device_id>', methods=['GET'])
def device_settings(device_id: int):
    with DB.connect() as db:
        device = get_device(db, device_id)
        if not device:
            return error('Device not found')

        data, errors = DeviceSchema().dump(device)
        return jsonify(data) if not errors else internal_error()
