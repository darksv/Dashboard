from datetime import datetime
from tzlocal import get_localzone


def localize_datetime(dt: datetime) -> datetime:
    """
    Add local timezone to datetime.
    """
    return get_localzone().localize(dt)
