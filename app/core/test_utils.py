from .utils import datetimes_between
from datetime import timedelta as delta
from datetime import datetime


def test_datetimes_between_with_one_second():
    now = datetime.now().replace(microsecond=0)
    datetimes = datetimes_between(now, now + delta(seconds=5), 1)

    assert list(datetimes) == [
        now,
        now + delta(seconds=1),
        now + delta(seconds=2),
        now + delta(seconds=3),
        now + delta(seconds=4),
        now + delta(seconds=5),
    ]


def test_datetimes_between_with_one_minute():
    now = datetime.now().replace(microsecond=0)
    datetimes = datetimes_between(now, now + delta(minutes=5), 60)

    assert list(datetimes) == [
        now,
        now + delta(minutes=1),
        now + delta(minutes=2),
        now + delta(minutes=3),
        now + delta(minutes=4),
        now + delta(minutes=5),
    ]


def test_datetimes_between_with_some_minutes():
    now = datetime.now().replace(microsecond=0)
    datetimes = datetimes_between(now, now + delta(minutes=5), 120)

    assert list(datetimes) == [
        now,
        now + delta(minutes=2),
        now + delta(minutes=4),
    ]
