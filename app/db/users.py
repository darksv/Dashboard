from typing import Optional
from sqlalchemy import select
from app.db import Database, USERS
from app.models.user import User


def get_user_by_id(db: Database, user_id: int) -> Optional[User]:
    """
    Get user by ID.
    """
    query = select(USERS.c).select_from(USERS).where(USERS.c.id == user_id)
    result = db.execute(query)

    row = result.fetchone()

    if row is None:
        return None

    return User(row['id'], row['name'], row['hash'])


def get_user_by_username(db: Database, name: str) -> Optional[User]:
    """
    Get user by username.
    """
    query = select(USERS.c).select_from(USERS).where(USERS.c.name == name)
    result = db.execute(query)

    row = result.fetchone()

    if row is None:
        return None

    return User(row['id'], row['name'], row['hash'])
