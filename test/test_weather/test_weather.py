# coding=utf-8
from hypothesis import given, strategies as st, example

from emiz.weather import MissionWeather


@given(heading=st.integers(min_value=0, max_value=359))
def test_reverse_direction(heading):
    val = MissionWeather.reverse_direction(heading)
    assert 0 <= val <= 359
    assert val == heading - 180 or val == heading + 180
    assert type(val) is int


@given(heading=st.integers(min_value=-2000, max_value=2000))
def test_normalize_direction(heading):
    val = MissionWeather._normalize_direction(heading)
    assert 0 <= val <= 359
    assert type(val) is int


@given(base_speed=st.integers(min_value=0, max_value=40))
@example(base_speed=120)
@example(base_speed=-1)
def test_deviate_wind_speed(base_speed):
    val = MissionWeather._deviate_wind_speed(base_speed)
    assert 0 <= val <= 50
    assert type(val) is int