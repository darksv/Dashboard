from datetime import datetime
from operator import and_
from typing import Optional, List
from sqlalchemy import insert, select
from sqlalchemy.engine import Connection
from core.models import NOTIFICATIONS
from core.models.notification import Notification
from core.utils import map_object


def create_notification(db: Connection, user_id: int, message: str, trigger_id: int = None) -> Optional[int]:
    """
    Create new notification.
    """
    query = insert(NOTIFICATIONS).values(
        user_id=user_id,
        trigger_id=trigger_id,
        message=message,
        created=datetime.now()
    )
    result = db.execute(query)
    return result.lastrowid


def get_notification(db: Connection, notification_id: int) -> Optional[Notification]:
    """
    Get notification by id.
    """
    query = select(NOTIFICATIONS.c, NOTIFICATIONS.c.id == notification_id)
    result = db.execute(query)
    row = result.fetchone()
    return map_object(Notification, row) if row else None


def get_pending_notifications(db: Connection, user_id: int) -> List[Notification]:
    """
    Get all pending notifications for specified user.
    """
    query = select(NOTIFICATIONS.c, and_(NOTIFICATIONS.c.user_id == user_id, NOTIFICATIONS.c.received.is_(None)))
    result = db.execute(query)
    return [map_object(Notification, row) for row in result]
