from typing import Optional
from sqlalchemy import select
from core import Database
from core.models import USERS
from core.models.user import User
from core.utils import map_object


def get_user_by_id(db: Database, user_id: int) -> Optional[User]:
    """
    Get user by ID.
    """
    query = select(USERS.c).select_from(USERS).where(USERS.c.id == user_id)
    result = db.execute(query)
    row = result.fetchone()
    return map_object(User, row) if row else None


def get_user_by_username(db: Database, name: str) -> Optional[User]:
    """
    Get user by username.
    """
    query = select(USERS.c).select_from(USERS).where(USERS.c.name == name)
    result = db.execute(query)
    row = result.fetchone()
    return map_object(User, row) if row else None
