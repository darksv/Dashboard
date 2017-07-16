from datetime import datetime


class Notification:
    def __init__(self, id: int = None, user_id: int = None, watcher_id: int = None,
                 created: datetime = None, received: datetime = None, message: str = None):
        self._id = id
        self._user_id = user_id
        self._watcher_id = watcher_id
        self._created = created
        self._received = received
        self._message = message

    @property
    def id(self):
        return self._id

    @property
    def user_id(self):
        return self._user_id

    @property
    def watcher_id(self):
        return self._watcher_id

    @property
    def created(self):
        return self._created

    @property
    def received(self):
        return self._received

    @property
    def message(self):
        return self._message
