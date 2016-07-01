from datetime import datetime
from typing import Any, Callable, Optional, Tuple
from iso8601 import parse_date, ParseError
from tzlocal import get_localzone


def convert_in_dict(dct: dict, key: Any, mapper: Callable) -> None:
    dct[key] = mapper(dct[key])


def format_datetime(value: Tuple[str, datetime], dt_format: str='%H:%M:%S') -> Optional[str]:
    """
    Converts ISO8601 string or datetime object to specified format.
    """
    dt = value

    if isinstance(value, str):
        try:
            dt = parse_date(value)
        except ParseError:
            pass

    if not isinstance(dt, datetime):
        raise ValueError('Cannot convert {0} to datetime'.format(value))

    return dt.strftime(dt_format) if isinstance(dt, datetime) else None


def extract_keys(d: dict, keys) -> dict:
    """
    Creates new dict based on specified keys from list.
    """
    result = dict()

    for key in keys:
        result[key] = d[key]

    return result


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

