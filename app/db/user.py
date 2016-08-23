from flask_login import UserMixin
import werkzeug.security as ws


class User(UserMixin):
    def __init__(self, user_id: int = None, name: str = None, pwd_hash: str = None):
        self._id = user_id
        self._name = name
        self._hash = pwd_hash

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def hash(self):
        return self._hash

    def check_password(self, password: str):
        return ws.check_password_hash(self.hash, password)

    def save(self):
        pass
