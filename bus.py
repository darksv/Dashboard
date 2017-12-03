import logging
from collections import defaultdict


logger = logging.getLogger(__name__)


class Bus:
    def __init__(self):
        self._listeners = defaultdict(set)

    async def emit(self, event, data=None):
        for listener in self._listeners[event]:
            try:
                await listener(event, data)
            except Exception as e:
                logger.exception(e)

    def on(self, event):
        def wrapper(fn):
            self._listeners[event].add(fn)
            return fn
        return wrapper
