# coding=utf-8
"""
Tests Group object
"""

import pytest

from emiz.mission import BaseUnit, Group
from emiz.miz import Miz


def test_groups(mission):
    value = 0
    for group in mission.blue_coa.groups:
        value += 1
        assert isinstance(group, Group)
    assert value == 3
    value = 0
    for group in mission.red_coa.groups:
        value += 1
        assert isinstance(group, Group)
    assert value == 33


def test_get_groups_from_category(mission, all_objects):
    for invalid_category in ('caribou', 'Plane', 'plAne', 'ships', -1, 0, 1, True, False, None):
        with pytest.raises(ValueError):
            for _ in mission.blue_coa.get_groups_from_category(invalid_category):
                pass
    with Miz(all_objects) as miz:
        for category in ('ship', 'plane', 'helicopter', 'vehicle'):
            value = 0
            for group in miz.mission._blue_coa.get_groups_from_category(category):
                assert isinstance(group, Group)
                assert group.group_category == category
                value += 1
            assert value == 1


def test_get_group_by_id(mission):
    for group_id in range(1, 3):
        assert isinstance(mission.blue_coa.get_group_by_id(group_id), Group)
    for group_id in range(4, 36):
        assert isinstance(mission.red_coa.get_group_by_id(group_id), Group)
    for wrong_group_id in (-1, False, None, True, 'caribou'):
        with pytest.raises(ValueError, msg=wrong_group_id):
            mission.red_coa.get_group_by_id(wrong_group_id)
    for non_existing_group_id in (37, 50, 100, 150, mission.next_group_id):
        assert mission.red_coa.get_group_by_id(non_existing_group_id) is None
        assert mission.blue_coa.get_group_by_id(non_existing_group_id) is None


def test_group_by_name(mission):
    for group_name in ('etcher', 'gal', 'gilles'):
        assert isinstance(mission.blue_coa.get_group_by_name(group_name), Group)
    for i in range(1, 33):
        assert isinstance(mission.red_coa.get_group_by_name('New Vehicle Group #{}'.format(str(i).zfill(3))),
                          Group)
    for wrong_group_name in (-1, 0, 1, False, True, None):
        with pytest.raises(ValueError, msg=wrong_group_name):
            mission.blue_coa.get_group_by_name(wrong_group_name)
    for non_existing_group_name in ('yup', 'yop', 'New Vehicle group #019', 'Gilles', 'etcheR'):
        assert mission.red_coa.get_group_by_name(non_existing_group_name) is None
        assert mission.blue_coa.get_group_by_name(non_existing_group_name) is None


def test_set_hidden(test_file, out_file):
    with Miz(test_file) as miz:
        group = miz.mission.get_group_by_name('etcher')
        assert isinstance(group, Group)
        assert not group.group_hidden
        group.group_hidden = True
        assert group.group_hidden
        miz.zip(out_file)
    with Miz(out_file) as miz:
        new_group = miz.mission.get_group_by_name('etcher')
        assert isinstance(new_group, Group)
        for attrib in [x for x in Group.attribs if not x == 'group_hidden']:
            assert getattr(group, attrib) == getattr(new_group, attrib)
        assert group.group_hidden


def test_get_unit(mission):
    group = mission.get_group_by_name('etcher')
    assert isinstance(group, Group)
    unit1 = group.get_unit_by_name('etcher')
    assert isinstance(unit1, BaseUnit)
    unit2 = group.get_unit_by_id(1)
    assert isinstance(unit2, BaseUnit)
    unit3 = group.get_unit_by_index(1)
    assert isinstance(unit3, BaseUnit)
    assert unit1 == unit2 == unit3


def test_get_group_by_name(mission):
    group = mission.get_group_by_name('etcher')
    assert isinstance(group, Group)
    assert group.group_id == 1
    assert mission.get_group_by_name('le_caribou_puissant') is None
