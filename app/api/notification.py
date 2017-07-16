from flask import jsonify, request
from api import api_auth_required, api_user, app, internal_error
from api.schemas.notification import NotificationSchema
from core import DB
from core.services.notification import create_notification, get_pending_notifications


@app.route('/api/notification', methods=['POST'])
def new_notification():
    data, errors = NotificationSchema().load(request.get_json() or request.args)
    if errors:
        return jsonify(errors=errors)

    user_id = data['user_id']
    watcher_id = data['watcher_id']
    message = data['message']

    notification_id = create_notification(DB, user_id, message, watcher_id)
    if not notification_id:
        return internal_error()

    return jsonify()


@app.route('/api/notifications', methods=['GET'])
@api_auth_required
def api_notifications():
    notifications = get_pending_notifications(DB, api_user.id)
    return jsonify(notifications=NotificationSchema().dump(notifications, many=True).data)
