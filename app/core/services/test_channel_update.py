from datetime import datetime, timedelta
from unittest import TestCase

import pytest

from core.services.channel_update import AverageCalculator, average


class TestAverageCalculator(TestCase):
    def test_push_value_should_store_the_value(self):
        calculator = AverageCalculator(period=60, start_at=datetime.now())
        calculator.push_value(1, datetime.now())
        assert calculator.values == [1]

    def test_push_value_should_clear_values_when_period_elapsed(self):
        calculator = AverageCalculator(period=60, start_at=datetime.now())
        calculator.push_value(2, datetime.now())
        calculator.push_value(1, datetime.now() + timedelta(seconds=61))
        assert calculator.values == [1]

    def test_has_average_should_return_false_when_period_didnt_elapse(self):
        calculator = AverageCalculator(period=60, start_at=datetime.now())
        calculator.push_value(1, datetime.now())
        assert calculator.has_average is False

    def test_has_average_should_return_true_when_period_elapsed(self):
        calculator = AverageCalculator(period=60, start_at=datetime.now())
        calculator.push_value(2, datetime.now())
        calculator.push_value(1, datetime.now() + timedelta(seconds=61))
        assert calculator.has_average is True

    def test_pop_average_should_return_average(self):
        calculator = AverageCalculator(period=60, start_at=datetime.now())
        calculator.push_value(2, datetime.now())
        calculator.push_value(1, datetime.now() + timedelta(seconds=61))
        value, _ = calculator.pop_average()
        assert value == 2

    def test_pop_average_should_return_timestamp_in_the_middle_of_period(self):
        now = datetime(2017, 2, 2, 10, 0, 10)
        calculator = AverageCalculator(period=60, start_at=now)
        calculator.push_value(2, now + timedelta(seconds=20))
        calculator.push_value(10, now + timedelta(seconds=70))
        _, actual = calculator.pop_average()
        expected = now + timedelta(seconds=30)
        assert actual == expected

    def test_calculator_should_work_for_multiple_periods(self):
        now = datetime(2017, 2, 2, 10, 0, 10)
        calculator = AverageCalculator(period=60, start_at=now)
        calculator.push_value(2, now + timedelta(seconds=20))
        calculator.push_value(10, now + timedelta(seconds=70))
        calculator.push_value(15, now + timedelta(seconds=75))
        calculator.push_value(20, now + timedelta(seconds=127))
        actual = calculator.pop_average()
        expected = (12.5, now + timedelta(seconds=90))
        assert actual == expected

    def test_pop_average_should_raise_exception_when_no_average_to_pop(self):
        now = datetime(2017, 2, 2, 10, 0, 10)
        calculator = AverageCalculator(period=60, start_at=now)
        with pytest.raises(RuntimeError):
            calculator.pop_average()


def test_average_should_return_none_for_empty_list():
    assert average([]) is None


def test_average_should_return_valid_average_of_numbers():
    assert average([3, 1, 2]) == 2


def test_average_should_drop_minimal_and_maximal_value_when_there_is_more_than_four_values():
    assert average([0, 2, 3, 4, 1000]) == 3

