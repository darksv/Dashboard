from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy import create_engine

meta = MetaData()

SENSORS = Table('sensors', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('internal_id', String(50), unique=True),
    Column('type', Integer, nullable=False),
    Column('title', String(100), nullable=False, default='')
)


class Database:
    def __init__(self, db_uri: str):
        self._engine = create_engine(db_uri, echo=True)
        self._connection = self._engine.connect()

        self.create()

    def create(self):
        meta.create_all(bind=self._engine)

    @property
    def conn(self):
        return self._connection
