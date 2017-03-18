from datetime import datetime
from operator import and_
from typing import Optional, List
from sqlalchemy import insert, select
from app.db import Database, NOTIFICATIONS
from app.models.notification import Notification


def create_notification(db: Database, user_id: int, message: str, watcher_id: int = None) -> Optional[int]:
    """
    Create new notification.
    """
    query = insert(NOTIFICATIONS).values(
        user_id=user_id,
        watcher_id=watcher_id,
        message=message,
        created=datetime.now()
    )
    result = db.execute(query)

    return result.lastrowid


def get_notification(db: Database, notification_id: int) -> Optional[Notification]:
    """
    Get notification by id.
    """
    query = select(NOTIFICATIONS.c, NOTIFICATIONS.c.id == notification_id)
    result = db.execute(query)

    return Notification(*result.fetchone())


def get_pending_notifications(db: Database, user_id: int) -> List[Notification]:
    """
    Get all pending notifications for specified user.
    """
    query = select(NOTIFICATIONS.c, and_(NOTIFICATIONS.c.user_id == user_id, NOTIFICATIONS.c.received == None))
    result = db.execute(query)

    return [Notification(*row) for row in result]
