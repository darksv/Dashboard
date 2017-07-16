import math
from collections import defaultdict
from datetime import datetime, timedelta
from app import get_channel, update_channel
from app.db.channels import log_channel_value


def average(values):
    """
    Calculates average of list of values. Ignores the lowest and the greatest values when there is enough data.
    """
    if len(values) > 4:
        values.sort()
        values = values[1:-1]

    return sum(values) / len(values) if values else None


calculators = defaultdict(lambda: AverageCalculator(
    period=60,
    start_at=datetime.now().replace(second=0, microsecond=0)
))


def process_channel_update(db, channel_id, new_value):
    """
    Handle .
    """
    channel = get_channel(db, channel_id)
    if channel is None:
        return

    trans = db.conn.begin()
    try:
        calculator = calculators[channel.id]
        calculator.push_value(new_value)
        if calculator.has_average:
            value, timestamp = calculator.pop_average()
            log_channel_value(db, channel.id, value, timestamp, ignore_duplicates=True)
        update_channel(db, channel.id, value=new_value, value_updated=datetime.now())
        trans.commit()
    except:
        trans.rollback()
        raise


class AverageCalculator:
    def __init__(self, period=60, start_at=None):
        self.__period = period
        self.__start_at = start_at if start_at is not None else datetime.now()
        self.__values = []
        self.__average = None

    def push_value(self, value, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        previous_period = self.__period_number(self.__values[-1][1]) if self.has_values else None
        current_period = self.__period_number(timestamp)

        if previous_period is not None and previous_period != current_period:
            self.__average = average(self.values), self.__period_timestamp(previous_period)
            self.__values.clear()

        self.__push_value(value, timestamp)

    def pop_average(self):
        if not self.has_average:
            raise RuntimeError('No calculated average')

        result = self.__average
        self.__average = None
        return result

    def __push_value(self, value, timestamp):
        self.__values.append((value, timestamp))

    def __period_number(self, timestamp):
        elapsed = (timestamp - self.__start_at).total_seconds()
        return math.floor(elapsed / self.__period)

    def __period_timestamp(self, period_number):
        return self.__start_at + timedelta(seconds=(period_number + 0.5) * self.__period)

    @property
    def has_average(self):
        return self.__average is not None

    @property
    def has_values(self):
        return len(self.__values) > 0

    @property
    def values(self):
        return [value for value, timestamp in self.__values]
