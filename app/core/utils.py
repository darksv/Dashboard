import inspect
import re
from datetime import datetime, timedelta
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


def parse_datetime(dt: str) -> datetime:
    """
    Convert YYYYMMDDHHMM format string to datetime.
    """
    if not (isinstance(dt, str) and len(dt) == 12 and dt.isdigit()):
        raise ValueError('Invalid format {0}'.format(dt))

    year, month, day, hour, minute = \
        map(int, (dt[0:4], dt[4:6], dt[6:8], dt[8:10], dt[10:12]))

    return datetime(year, month, day, hour, minute)


def parse_time_interval(s: str) -> Tuple[int, str]:
    """
    Parse value with suffix.

    Available suffixes:
     s - seconds
     m - minutes
     h - hours
     d - days
     M - months
     y - years
    """
    suffixes = {
        's': 'seconds',
        'm': 'minutes',
        'h': 'hours',
        'd': 'days',
        'M': 'months',
        'y': 'years'
    }

    expr = re.compile('(\d+)([{0}])'.format(''.join(suffixes.keys())))
    match = expr.match(s)

    if match is None:
        raise ValueError('Invalid format {0}'.format(s))

    value, suffix = match.groups()

    return int(value), suffixes[suffix]


def parse_color(s: str) -> Tuple[int, int, int]:
    """
    Parse color in hexadecimal string into a tuple of RGB values.
    """
    if s.startswith('#'):
        s = s[1:]

    try:
        if len(s) == 3:
            r = s[0] * 2
            g = s[1] * 2
            b = s[2] * 2
        elif len(s) == 6:
            r = s[0:2]
            g = s[2:4]
            b = s[4:6]
        else:
            r = ''
            g = ''
            b = ''
        value = tuple(map(lambda x: int(x, 16), [r, g, b]))
    except ValueError:
        raise ValueError('Invalid color format')
    else:
        return value


def hours_between_dates(start: datetime, end: datetime):
    """
    Generates datetimes between two other with one hour interval.
    """
    yield from datetimes_between(start, end, 3600)


def minutes_between_dates(start: datetime, end: datetime):
    """
    Generates datetimes between two other with one minute interval.
    """
    yield from datetimes_between(start, end, 60)


def datetimes_between(start: datetime, end: datetime, interval: int):
    """
    Generates datetimes between two other with given interval in seconds.
    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    delta = end - start
    for seconds in range(0, int(delta.total_seconds()) + 1, interval):
        yield start + timedelta(seconds=seconds)


def map_object(cls, dct):
    """
    Maps dict to object of given class.
    """
    return cls(**extract_keys(dct, [x for x in inspect.signature(cls).parameters]))
