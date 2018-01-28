# coding=utf-8
"""
Tests global mission functionality
"""
import pytest

from emiz.mission import BaseUnit, Coalition, Country, Group, Static
from emiz.miz import Miz


def test_bullseye(mission):
    assert (11557, 371700) == mission.red_coa.bullseye_position
    assert (-291014, 617414) == mission.blue_coa.bullseye_position


def test_ln10(mission):
    import pprint
    assert mission.l10n == {'DictKey_GroupName_101': 'New Vehicle Group #029',
                            'DictKey_GroupName_104': 'New Vehicle Group #030',
                            'DictKey_GroupName_107': 'New Vehicle Group #031',
                            'DictKey_GroupName_11': 'gilles',
                            'DictKey_GroupName_110': 'New Vehicle Group #032',
                            'DictKey_GroupName_113': 'New Static Object',
                            'DictKey_GroupName_116': 'New Static Object #001',
                            'DictKey_GroupName_119': 'New Static Object #002',
                            'DictKey_GroupName_122': 'New Static Object #003',
                            'DictKey_GroupName_125': 'New Static Object #004',
                            'DictKey_GroupName_14': 'New Vehicle Group',
                            'DictKey_GroupName_17': 'New Vehicle Group #001',
                            'DictKey_GroupName_20': 'New Vehicle Group #002',
                            'DictKey_GroupName_23': 'New Vehicle Group #003',
                            'DictKey_GroupName_26': 'New Vehicle Group #004',
                            'DictKey_GroupName_29': 'New Vehicle Group #005',
                            'DictKey_GroupName_32': 'New Vehicle Group #006',
                            'DictKey_GroupName_35': 'New Vehicle Group #007',
                            'DictKey_GroupName_38': 'New Vehicle Group #008',
                            'DictKey_GroupName_41': 'New Vehicle Group #009',
                            'DictKey_GroupName_44': 'New Vehicle Group #010',
                            'DictKey_GroupName_47': 'New Vehicle Group #011',
                            'DictKey_GroupName_5': 'etcher',
                            'DictKey_GroupName_50': 'New Vehicle Group #012',
                            'DictKey_GroupName_53': 'New Vehicle Group #013',
                            'DictKey_GroupName_56': 'New Vehicle Group #014',
                            'DictKey_GroupName_59': 'New Vehicle Group #015',
                            'DictKey_GroupName_62': 'New Vehicle Group #016',
                            'DictKey_GroupName_65': 'New Vehicle Group #017',
                            'DictKey_GroupName_68': 'New Vehicle Group #018',
                            'DictKey_GroupName_71': 'New Vehicle Group #019',
                            'DictKey_GroupName_74': 'New Vehicle Group #020',
                            'DictKey_GroupName_77': 'New Vehicle Group #021',
                            'DictKey_GroupName_8': 'gal',
                            'DictKey_GroupName_80': 'New Vehicle Group #022',
                            'DictKey_GroupName_83': 'New Vehicle Group #023',
                            'DictKey_GroupName_86': 'New Vehicle Group #024',
                            'DictKey_GroupName_89': 'New Vehicle Group #025',
                            'DictKey_GroupName_92': 'New Vehicle Group #026',
                            'DictKey_GroupName_95': 'New Vehicle Group #027',
                            'DictKey_GroupName_98': 'New Vehicle Group #028',
                            'DictKey_UnitName_102': 'Unit #029',
                            'DictKey_UnitName_105': 'Unit #030',
                            'DictKey_UnitName_108': 'Unit #031',
                            'DictKey_UnitName_111': 'Unit #032',
                            'DictKey_UnitName_114': '',
                            'DictKey_UnitName_117': '',
                            'DictKey_UnitName_12': 'gilles',
                            'DictKey_UnitName_120': '',
                            'DictKey_UnitName_123': '',
                            'DictKey_UnitName_126': '',
                            'DictKey_UnitName_15': 'Unit #1',
                            'DictKey_UnitName_18': 'Unit #001',
                            'DictKey_UnitName_21': 'Unit #002',
                            'DictKey_UnitName_24': 'Unit #003',
                            'DictKey_UnitName_27': 'Unit #004',
                            'DictKey_UnitName_30': 'Unit #005',
                            'DictKey_UnitName_33': 'Unit #006',
                            'DictKey_UnitName_36': 'Unit #007',
                            'DictKey_UnitName_39': 'Unit #008',
                            'DictKey_UnitName_42': 'Unit #009',
                            'DictKey_UnitName_45': 'Unit #010',
                            'DictKey_UnitName_48': 'Unit #011',
                            'DictKey_UnitName_51': 'Unit #012',
                            'DictKey_UnitName_54': 'Unit #013',
                            'DictKey_UnitName_57': 'Unit #014',
                            'DictKey_UnitName_6': 'etcher',
                            'DictKey_UnitName_60': 'Unit #015',
                            'DictKey_UnitName_63': 'Unit #016',
                            'DictKey_UnitName_66': 'Unit #017',
                            'DictKey_UnitName_69': 'Unit #018',
                            'DictKey_UnitName_72': 'Unit #019',
                            'DictKey_UnitName_75': 'Unit #020',
                            'DictKey_UnitName_78': 'Unit #021',
                            'DictKey_UnitName_81': 'Unit #022',
                            'DictKey_UnitName_84': 'Unit #023',
                            'DictKey_UnitName_87': 'Unit #024',
                            'DictKey_UnitName_9': 'gal',
                            'DictKey_UnitName_90': 'Unit #025',
                            'DictKey_UnitName_93': 'Unit #026',
                            'DictKey_UnitName_96': 'Unit #027',
                            'DictKey_UnitName_99': 'Unit #028',
                            'DictKey_WptName_10': '',
                            'DictKey_WptName_100': '',
                            'DictKey_WptName_103': '',
                            'DictKey_WptName_106': '',
                            'DictKey_WptName_109': '',
                            'DictKey_WptName_112': '',
                            'DictKey_WptName_115': '',
                            'DictKey_WptName_118': '',
                            'DictKey_WptName_121': '',
                            'DictKey_WptName_124': '',
                            'DictKey_WptName_127': '',
                            'DictKey_WptName_13': '',
                            'DictKey_WptName_16': '',
                            'DictKey_WptName_19': '',
                            'DictKey_WptName_22': '',
                            'DictKey_WptName_25': '',
                            'DictKey_WptName_28': '',
                            'DictKey_WptName_31': '',
                            'DictKey_WptName_34': '',
                            'DictKey_WptName_37': '',
                            'DictKey_WptName_40': '',
                            'DictKey_WptName_43': '',
                            'DictKey_WptName_46': '',
                            'DictKey_WptName_49': '',
                            'DictKey_WptName_52': '',
                            'DictKey_WptName_55': '',
                            'DictKey_WptName_58': '',
                            'DictKey_WptName_61': '',
                            'DictKey_WptName_64': '',
                            'DictKey_WptName_67': '',
                            'DictKey_WptName_7': '',
                            'DictKey_WptName_70': '',
                            'DictKey_WptName_73': '',
                            'DictKey_WptName_76': '',
                            'DictKey_WptName_79': '',
                            'DictKey_WptName_82': '',
                            'DictKey_WptName_85': '',
                            'DictKey_WptName_88': '',
                            'DictKey_WptName_91': '',
                            'DictKey_WptName_94': '',
                            'DictKey_WptName_97': '',
                            'DictKey_descriptionBlueTask_3': '',
                            'DictKey_descriptionRedTask_2': '',
                            'DictKey_descriptionText_1': '',
                            'DictKey_sortie_4': 'sortie_test'}, pprint.pprint(mission.l10n)


def test_name(mission):
    assert 'blue' == mission.blue_coa.coalition_name
    assert 'red' == mission.red_coa.coalition_name


def test_ground_control(mission):
    assert not mission.ground_control.pilots_control_vehicles
    mission.ground_control.pilots_control_vehicles = True
    assert mission.ground_control.pilots_control_vehicles
    for attrib in [
        'artillery_commander_blue',
        'artillery_commander_red',
        'forward_observer_blue',
        'forward_observer_red',
        'instructor_blue',
        'instructor_red',
        'observer_red',
        'observer_blue',
    ]:
        assert getattr(mission.ground_control, attrib) == 0
        for wrong_param in [-1, 101, True, None, 'caribou']:
            with pytest.raises(ValueError, msg=wrong_param):
                setattr(mission.ground_control, attrib, wrong_param)
        for i in range(0, 60, 5):
            setattr(mission.ground_control, attrib, i)


def test_objects(all_objects):
    with Miz(all_objects) as miz:
        _ = miz.mission._blue_coa.get_country_by_id(2)
        country = miz.mission._blue_coa.get_country_by_id(2)
        assert isinstance(country, Country)
        assert country.groups
        assert country.units
        for category in ('helicopter', 'ship', 'vehicle', 'plane'):
            assert country.get_groups_from_category(category)
            assert country.get_units_from_category(category)
            for group in country.get_groups_from_category(category):
                assert isinstance(group, Group)
            for unit in country.get_units_from_category(category):
                assert isinstance(unit, BaseUnit)
        for wrong_category in (True, -1, 0, 1, False, None, 'caribou'):
            with pytest.raises(ValueError, msg=wrong_category):
                for _ in country.get_groups_from_category(wrong_category):
                    pass
            with pytest.raises(ValueError, msg=wrong_category):
                for _ in country.get_units_from_category(wrong_category):
                    pass
        for id_ in (1, 2, 3, 4):
            assert isinstance(country.get_group_by_id(id_), Group)
            assert isinstance(country.get_unit_by_id(id_), BaseUnit)
        assert country.get_unit_by_id(5) is None
        assert country.get_group_by_id(5) is None
        for group_name in ('New Vehicle Group', 'New Helicopter Group', 'New Airplane Group', 'New Ship Group'):
            assert isinstance(country.get_group_by_name(group_name), Group)
        assert country.get_group_by_name('some other group') is None
        for unit_name in ('Unit #1', 'Unit #001', 'Pilot #001', 'Pilot #002'):
            assert isinstance(country.get_unit_by_name(unit_name), BaseUnit)
        assert country.get_unit_by_name('some other unit') is None


def test_coalitions_generator(mission):
    assert mission.coalitions
    value = 0
    for coa in mission.coalitions:
        assert isinstance(coa, Coalition)
        value += 1
    assert value == 2


def test_repr(mission):
    assert 'Mission({})'.format(mission.d) == mission.__repr__()


def test_next_group_id(mission, duplicate_group_id):
    assert mission.next_group_id == 37
    with pytest.raises(IndexError):
        with Miz(duplicate_group_id) as miz:
            assert miz.mission.next_group_id


def test_next_unit_id(mission, duplicate_group_id):
    assert mission.next_unit_id == 37
    with pytest.raises(IndexError):
        with Miz(duplicate_group_id) as miz:
            assert miz.mission.next_unit_id


def test_sortie_name(test_file, out_file):
    with Miz(test_file) as miz:
        assert miz.mission.sortie_name == 'sortie_test'
        wrong_sortie_names = [1, 0, -1, True, None]
        for wrong_sortie_name in wrong_sortie_names:
            with pytest.raises(ValueError):
                miz.mission.sortie_name = wrong_sortie_name
        miz.mission.sortie_name = 'caribou'
        assert miz.mission.sortie_name == 'caribou'
        miz.zip(out_file)
    with Miz(out_file) as miz:
        assert miz.mission.sortie_name == 'caribou'


def test_farps(mission):
    assert len(list(mission.farps())) > 0
    for farp in mission.farps():
        assert isinstance(farp, Static)
