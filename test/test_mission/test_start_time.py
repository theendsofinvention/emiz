# coding=utf-8
"""
Tests start time
"""

import pytest
from hypothesis import strategies as st
from hypothesis import given, settings

from emiz.miz import Miz


@given(time=st.integers(0, 86399))
@settings(max_examples=1)
def test_mission_start_time(time, mission):
    assert mission.mission_start_time == 43200
    assert mission.mission_start_datetime_as_string == '01/06/2011 12:00:00'
    mission.mission_start_time = 0
    assert mission.mission_start_datetime_as_string == '01/06/2011 00:00:00'
    mission.mission_start_time = time


@given(time=st.integers(min_value=86400))
@settings(max_examples=1)
def test_wrong_mission_start_time(time, mission):
    with pytest.raises(ValueError):
        mission.mission_start_time = time


@given(time=st.integers(max_value=-1))
@settings(max_examples=1)
def test_wrong_mission_start_time_neg(time, mission):
    with pytest.raises(ValueError):
        mission.mission_start_time = time


def test_group_start_time(test_file, out_file):
    with Miz(test_file) as miz:
        group = miz.mission.get_group_by_name('etcher')
        assert miz.mission.mission_start_time == group.group_start_time
        assert miz.mission.mission_start_datetime_as_string == group.group_start_date_time_as_string
        assert group.group_start_date_time_as_string == '01/06/2011 12:00:00'
        assert group.group_start_delay == 0
        group.group_start_delay += 60
        assert group.group_start_date_time_as_string == '01/06/2011 12:01:00'
        group.group_start_delay += 3600
        assert group.group_start_date_time_as_string == '01/06/2011 13:01:00'
        group.group_start_delay = 0
        group.group_start_delay = 3600
        assert group.group_start_date_time_as_string == '01/06/2011 13:00:00'
        miz.zip(out_file)

    with Miz(out_file) as miz:
        group = miz.mission.get_group_by_name('etcher')
        assert group.group_start_delay == 3600
