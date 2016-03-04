from datetime import datetime
from tzlocal import get_localzone


def localize_datetime(dt: datetime) -> datetime:
    """
    Add local timezone to datetime.
    """
    return get_localzone().localize(dt)


def convert_datetime_to_iso(dt: datetime) -> str:
    """
    Convert datetime to ISO8601 string.
    """
    return localize_datetime(dt).isoformat()
