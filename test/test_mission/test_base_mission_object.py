# coding=utf-8
"""
Tests BaseMissionObject
"""

import pytest

from emiz.mission import BaseMissionObject, BaseUnit, Group


def test_init():
    with pytest.raises(TypeError):
        BaseMissionObject(None, {})
    with pytest.raises(TypeError):
        BaseMissionObject({}, None)
    BaseMissionObject({}, {})


def test_get_country_by_name(mission):
    with pytest.raises(ValueError):
        mission.get_country_by_name('nope')
    country = mission.get_country_by_name('USA')
    assert country is mission.get_country_by_name('USA')


def test_get_country_by_id(mission):
    with pytest.raises(ValueError):
        mission.get_country_by_id(9999)
    country = mission.get_country_by_id(1)
    assert country is mission.get_country_by_id(1)


@pytest.mark.parametrize('category', ['helicopter', 'ship', 'plane', 'vehicle'])
def test_get_groups_from_category(mission, category):
    with pytest.raises(ValueError):
        list(mission.get_groups_from_category(None))
    assert isinstance(list(mission.get_groups_from_category(category)), list)


@pytest.mark.parametrize('category', ['helicopter', 'ship', 'plane', 'vehicle'])
def test_get_units_from_category(mission, category):
    with pytest.raises(ValueError):
        list(mission.get_units_from_category(None))
    assert isinstance(list(mission.get_units_from_category(category)), list)


def test_get_group_by_id(mission):
    with pytest.raises(ValueError):
        mission.get_group_by_id(None)
    assert mission.get_group_by_id(99999) is None
    assert isinstance(mission.get_group_by_id(1), Group)


def test_get_unit_by_id(mission):
    with pytest.raises(ValueError):
        mission.get_unit_by_id(None)
    assert mission.get_unit_by_id(99999) is None
    assert isinstance(mission.get_unit_by_id(1), BaseUnit)


def test_get_clients_groups(mission):
    result = list(mission.get_clients_groups())
    assert len(result) == 3
    names = ['etcher', 'gal', 'gilles']
    for group in result:
        assert isinstance(group, Group)
        assert group.group_name in names


def test_day(mission):
    assert mission.day == 1
    mission.month = 2
    mission.day = 31
    assert mission.day == 28


@pytest.mark.parametrize('day', [-1, 100, None, '1'])
def test_wrong_day(mission, day):
    with pytest.raises(ValueError):
        mission.day = day


def test_month(mission):
    assert mission.month == 6
    mission.month = 2
    assert mission.month == 2


@pytest.mark.parametrize('month', [-1, 13, None, '1'])
def test_wrong_month(mission, month):
    with pytest.raises(ValueError):
        mission.month = month


def test_year(mission):
    assert mission.year == 2011
    mission.year = 2012
    assert mission.year == 2012


@pytest.mark.parametrize('year', [-1, 1899, 2101, 13, None, '1'])
def test_wrong_year(mission, year):
    with pytest.raises(ValueError):
        mission.year = year
