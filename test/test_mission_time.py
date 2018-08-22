# coding=utf-8
import datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from emiz import mission_time
from emiz.miz import Miz

_DUMMY_DT = datetime.datetime.now()


@given(example_datetime=st.datetimes(
    min_value=_DUMMY_DT.replace(year=1900),
    max_value=_DUMMY_DT.replace(year=2050),
))
@settings(max_examples=500)
def test_from_string(example_datetime: datetime.datetime):
    example_datetime = example_datetime.replace(tzinfo=None, microsecond=0)
    year = example_datetime.year
    month = example_datetime.month
    day = example_datetime.day
    hour = example_datetime.hour
    minute = example_datetime.minute
    second = example_datetime.second
    input_string = f'{year:04d}{month:02d}{day:02d}{hour:02d}{minute:02d}{second:02d}'
    time = mission_time.MissionTime.from_string(input_string)
    assert isinstance(time, mission_time.MissionTime)
    assert isinstance(time.date, datetime.date)
    assert time.date.year == year
    assert time.date.month == month
    assert time.date.day == day
    assert isinstance(time.time, datetime.time)
    assert time.time.hour == hour
    assert time.time.minute == minute
    assert time.time.second == second
    assert isinstance(time.mission_start_time, int)
    assert example_datetime == time.datetime


def test_now():
    now = datetime.datetime.now()
    now = now.replace(tzinfo=None, microsecond=0)
    time = mission_time.MissionTime.now()
    assert time.datetime - now <= datetime.timedelta(seconds=1)


@pytest.mark.long
@given(example_datetime=st.datetimes(
    min_value=_DUMMY_DT.replace(year=1900),
    max_value=_DUMMY_DT.replace(year=2050),
))
@settings(max_examples=10, deadline=1200)
def test_apply_to_miz(test_file, example_datetime):
    example_datetime = example_datetime.replace(tzinfo=None, microsecond=0)
    if example_datetime.day == 31:
        example_datetime = example_datetime.replace(day=30)
    year = example_datetime.year
    month = example_datetime.month
    day = example_datetime.day
    hour = example_datetime.hour
    minute = example_datetime.minute
    second = example_datetime.second
    input_string = f'{year:04d}{month:02d}{day:02d}{hour:02d}{minute:02d}{second:02d}'
    time = mission_time.MissionTime.from_string(input_string)
    with Miz(test_file) as miz:
        original_start_time = miz.mission.mission_start_time
        time.apply_to_miz(miz)
        assert miz.mission.mission_start_time != original_start_time
        assert miz.mission.day == time.date.day
        assert miz.mission.month == time.date.month
        assert miz.mission.year == time.date.year
        assert miz.mission.mission_start_time == time.mission_start_time
