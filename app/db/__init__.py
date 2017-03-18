from threading import RLock
from sqlalchemy import MetaData, Table, Binary, Column, Integer, String, SmallInteger, Text, ForeignKey, Float, DateTime, Boolean
from sqlalchemy import create_engine
import config

meta = MetaData()

DEVICES = Table('devices', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('uuid', Binary(16), nullable=False),
    Column('name', String(100), default='')
)

CHANNELS = Table('channels', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('uuid', Binary(16), nullable=False),
    Column('device_id', Integer, ForeignKey('devices.id'), nullable=False),
    Column('type', SmallInteger, nullable=False),
    Column('name', String(100), nullable=False, default=''),
    Column('value', Float),
    Column('value_updated', DateTime(timezone=True)),
    Column('unit', String(10), nullable=True, default=None),
    Column('color', String(7), nullable=True, default=None),
    Column('disabled', Boolean, default=False)
)

CHANNELS_ORDER = Table('channels_order', meta,
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('channel_id', Integer, ForeignKey('channels.id'), nullable=False),
    Column('order', Integer)
)

ENTRIES = Table('entries', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('channel_id', Integer, ForeignKey('channels.id'), nullable=False),
    Column('value', Float, nullable=False),
    Column('timestamp', DateTime(timezone=True), nullable=False)
)

USERS = Table('users', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(100), unique=True),
    Column('hash', String(100))
)

WATCHERS = Table('watchers', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('channel_id', Integer, ForeignKey('channels.id'), nullable=False),
    Column('condition', Text),
    Column('message', String(100)),
    Column('renew_time', Integer)
)

NOTIFICATIONS = Table('notifications', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('watcher_id', Integer, ForeignKey('watchers.id'), nullable=True),
    Column('created', DateTime(timezone=True)),
    Column('received', DateTime(timezone=True), nullable=True),
    Column('message', String(100))
)


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
