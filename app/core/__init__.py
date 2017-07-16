from threading import RLock
from sqlalchemy import create_engine
import config
from core.models import meta


class Database:
    def __init__(self, db_uri: str):
        self._engine = create_engine(db_uri, echo=False)
        self._connection = self._engine.connect()
        self._lock = RLock()

        self.create()

    def create(self):
        meta.create_all(bind=self._engine)

    def execute(self, obj, *args, **kwargs):
        with self._lock:
            return self.conn.execute(obj, *args, **kwargs)

    @property
    def conn(self):
        return self._connection

DB = Database(config.DATABASE_URL)
