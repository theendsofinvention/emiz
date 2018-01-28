# coding=utf-8
"""
Tests Unit objects
"""

import pytest

from emiz.mission import BaseUnit
from emiz.miz import Miz


def test_units(mission):
    value = 0
    for unit in mission.blue_coa.units:
        value += 1
        assert isinstance(unit, BaseUnit)
    assert value == 3
    value = 0
    for unit in mission.red_coa.units:
        value += 1
        assert isinstance(unit, BaseUnit)
    assert value == 33


def test_get_units_from_category(mission, all_objects):
    for invalid_category in ('caribou', 'Plane', 'plAne', 'ships', -1, 0, 1, True, False, None):
        with pytest.raises(ValueError):
            for _ in mission.blue_coa.get_units_from_category(invalid_category):
                pass
    with Miz(all_objects) as miz:
        # for unit in mission.blue_coa.units:
        #     print(unit.group_category)
        for category in ('ship', 'plane', 'helicopter', 'vehicle'):
            value = 0
            for unit in miz.mission._blue_coa.get_units_from_category(category):
                assert isinstance(unit, BaseUnit)
                assert unit.group_category == category
                value += 1
            assert value == 1


def test_get_unit_by_id(mission):
    for unit_id in range(1, 3):
        assert isinstance(mission.blue_coa.get_unit_by_id(unit_id), BaseUnit)
    for unit_id in range(4, 36):
        assert isinstance(mission.red_coa.get_unit_by_id(unit_id), BaseUnit)
    for wrong_unit_id in (-1, False, None, True, 'caribou'):
        with pytest.raises(ValueError, msg=wrong_unit_id):
            mission.red_coa.get_unit_by_id(wrong_unit_id)
    for non_existing_unit_id in (37, 50, 100, 150, mission.next_unit_id):
        assert mission.red_coa.get_group_by_id(non_existing_unit_id) is None
        assert mission.blue_coa.get_group_by_id(non_existing_unit_id) is None


def test_unit_by_name(mission):
    for unit_name in ('etcher', 'gal', 'gilles'):
        assert isinstance(mission.blue_coa.get_unit_by_name(unit_name), BaseUnit)
    for i in range(1, 33):
        assert isinstance(mission.red_coa.get_unit_by_name('Unit #{}'.format(str(i).zfill(3))), BaseUnit)
    for wrong_unit_name in (-1, 0, 1, False, True, None):
        with pytest.raises(ValueError, msg=wrong_unit_name):
            mission.blue_coa.get_unit_by_name(wrong_unit_name)
    for non_existing_unit_name in ('yup', 'yop', 'unit #017', 'Gilles', 'etcheR'):
        assert mission.red_coa.get_unit_by_name(non_existing_unit_name) is None
        assert mission.blue_coa.get_unit_by_name(non_existing_unit_name) is None


def test_get_unit_by_name(mission):
    unit = mission.get_unit_by_name('etcher')
    assert isinstance(unit, BaseUnit)
    assert unit.unit_id == 1
    assert mission.get_unit_by_name('le_caribou_puissant') is None
