class Watcher:
    def __init__(self, id: int = None, user_id: int = None, channel_id: int = None,
                 condition: str = None, message: str = None, renew_time: int = None):
        self._id = id
        self._user_id = user_id
        self._channel_id = channel_id
        self._condition = condition
        self._message = message
        self._renew_time = renew_time

    @property
    def id(self):
        return self._id

    @property
    def user_id(self):
        return self._user_id

    @property
    def channel_id(self):
        return self._channel_id

    @property
    def condition(self):
        return self._condition

    @property
    def message(self):
        return self._message

    @property
    def renew_time(self):
        return self._renew_time
