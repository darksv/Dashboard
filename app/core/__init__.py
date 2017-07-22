from contextlib import contextmanager
from threading import RLock
from sqlalchemy import create_engine
import config
from core.models import meta


class Database:
    def __init__(self, db_uri: str):
        self._engine = create_engine(db_uri, echo=False)
        self._lock = RLock()

        self.create()

    def create(self):
        meta.create_all(bind=self._engine)

    @contextmanager
    def connect(self):
        conn = self._engine.connect()
        yield conn
        conn.close()

DB = Database(config.DATABASE_URL)
