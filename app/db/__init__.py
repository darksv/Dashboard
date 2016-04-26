from sqlalchemy import MetaData, Table, Binary, Column, Integer, String, SmallInteger, Text, ForeignKey, Float, DateTime
from sqlalchemy import create_engine

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
    Column('value_updated', DateTime(timezone=True))
)

SENSORS = Table('sensors', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('internal_id', String(50), unique=True),
    Column('type', Integer, nullable=False),
    Column('name', String(100), nullable=False, default=''),
    Column('description', Text, nullable=False, default='')
)

ENTRIES = Table('entries', meta,
    Column('channel_id', Integer, ForeignKey('channels.id'), nullable=False),
    Column('value', Float, nullable=False),
    Column('timestamp', DateTime(timezone=True), nullable=False)
)


class Database:
    def __init__(self, db_uri: str):
        self._engine = create_engine(db_uri, echo=False)
        self._connection = self._engine.connect()

        self.create()

    def create(self):
        meta.create_all(bind=self._engine)

    @property
    def conn(self):
        return self._connection

DB = Database('')
