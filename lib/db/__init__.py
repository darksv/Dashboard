from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy import create_engine

meta = MetaData()

SENSORS = Table('sensors', meta,
    Column('id', Integer, primary_key=True),
    Column('type', Integer, nullable=False),
    Column('title', String(100))
)


class Database:
    def __init__(self):
        self._engine = create_engine('sqlite:///data.db')
        self._connection = self._engine.connect()

        self.create()

    def create(self):
        meta.create_all(bind=self._engine)

    @property
    def conn(self):
        return self._connection