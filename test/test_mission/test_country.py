# coding=utf-8
"""
Tests Country object
"""

import pytest

from emiz.mission import Country
from emiz.miz import Miz


def test_country_generator(mission):
    for coa in (mission.blue_coa, mission.red_coa):
        assert coa.countries
    value = 0
    for country in mission.blue_coa.countries:
        assert isinstance(country, Country)
        value += 1
    assert value in [19, 21]
    value = 0
    for country in mission.red_coa.countries:
        assert isinstance(country, Country)
        value += 1
    assert value in [10, 11]


def test_get_country_by_name(mission):
    assert isinstance(mission.blue_coa.get_country_by_name('USA'), Country)
    assert isinstance(mission.blue_coa.get_country_by_id(2), Country)
    assert isinstance(mission.blue_coa.get_country_by_name('USA'), Country)
    assert isinstance(mission.blue_coa.get_country_by_id(2), Country)
    for wrong_country_name in (1, -1, 0, False, None, True):
        with pytest.raises(ValueError, msg=wrong_country_name):
            mission.blue_coa.get_country_by_name(wrong_country_name)
    for wrong_country_id in (-1, False, None, True, 'caribou'):
        with pytest.raises(ValueError, msg=wrong_country_id):
            mission.blue_coa.get_country_by_id(wrong_country_id)
    for unknown_country_name in ('nope', 'nope too'):
        with pytest.raises(ValueError, msg=unknown_country_name):
            mission.blue_coa.get_country_by_name(unknown_country_name)
    for unknown_country_id in (150,):
        with pytest.raises(ValueError, msg=unknown_country_id):
            mission.blue_coa.get_country_by_id(unknown_country_id)


def test_get_country(mission, test_file):
    assert isinstance(mission.blue_coa.get_country_by_id(2), Country)
    assert isinstance(mission.blue_coa.get_country_by_name('USA'), Country)
    with pytest.raises(ValueError):
        mission.red_coa.get_country_by_name('USA')
    with pytest.raises(ValueError):
        mission.red_coa.get_country_by_id(2)
    with Miz(test_file) as miz:
        assert isinstance(miz.mission._blue_coa.get_country_by_name('USA'), Country)
