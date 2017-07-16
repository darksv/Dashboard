import flask_login
from flask import render_template, redirect, url_for, request, jsonify
from api.schemas.user import UserSchema
from core import DB
from core.services.channels import update_channels_order
from core.services.users import get_user_by_username
from . import app, api_auth_required, api_user


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    next_page = request.args.get('next', None)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = get_user_by_username(DB, username)

        if user and user.check_password(password):
            flask_login.login_user(user)

            return redirect(next_page or url_for('index'))
        else:
            message = ('error', 'Nieprawidłowe dane!')

    return render_template('login.html', message=message, next=next_page)


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(request.referrer or url_for('index'))


@app.route('/api/session')
def session():
    return jsonify(user=UserSchema().dump(flask_login.current_user).data)


@app.route('/api/order', methods=['POST'])
@api_auth_required
def api_update_order():
    ids = list(map(int, request.args.get('order', '').split(',')))
    update_channels_order(DB, api_user.id, ids)
    return jsonify()