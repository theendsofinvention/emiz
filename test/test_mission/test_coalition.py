# coding=utf-8
"""
Test coalition object
"""

import pytest

from emiz.mission import BaseUnit


def test_eq(mission):
    assert mission.blue_coa == mission.blue_coa
    with pytest.raises(ValueError):
        assert mission.blue_coa == mission.day


def test_statics(mission):
    blue_statics = list(mission.blue_coa.statics)
    red_statics = list(mission.red_coa.statics)
    assert len(blue_statics) == 3
    assert len(red_statics) == 2


def test_farps(mission):
    blue_farps = list(mission.blue_coa.farps)
    red_farps = list(mission.red_coa.farps)
    assert len(blue_farps) == len(red_farps) == 1


def get_unit_by_id(mission):
    assert mission.blue_coa.get_unit_by_id(9999) is None
    assert isinstance(mission.blue_coa.get_unit_by_id(1), BaseUnit)
