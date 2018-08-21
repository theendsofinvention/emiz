# coding=utf-8
import datetime

import pytest
from hypothesis import example, given
from hypothesis import strategies as st

import emiz.weather
from emiz.weather.mission_weather.mission_weather import _get_season


@given(heading=st.integers(min_value=0, max_value=359))
def test_reverse_direction(heading):
    val = emiz.weather.mission_weather.MissionWeather.reverse_direction(heading)
    assert 0 <= val <= 359
    assert val == heading - 180 or val == heading + 180
    assert type(val) is int


@given(heading=st.integers(min_value=-2000, max_value=2000))
def test_normalize_direction(heading):
    val = emiz.weather.mission_weather.MissionWeather._normalize_direction(heading)
    assert 0 <= val <= 359
    assert type(val) is int


@given(base_speed=st.integers(min_value=0, max_value=40))
@example(base_speed=120)
@example(base_speed=-1)
def test_deviate_wind_speed(base_speed):
    val = emiz.weather.mission_weather.MissionWeather._randomize_speed(base_speed)
    assert 0 <= val <= 50
    assert type(val) is int


@pytest.mark.parametrize(
    'date,season', [
        (datetime.date(2010, 1, 1), 'winter'),
        (datetime.date(2010, 4, 1), 'spring'),
        (datetime.date(2010, 7, 1), 'summer'),
        (datetime.date(2010, 10, 1), 'autumn'),
    ]
)
def test_get_season(date: datetime, season: str):
    result_season, result_temp = _get_season(_datetime=date)
    assert season == result_season
    assert isinstance(result_temp, int)
