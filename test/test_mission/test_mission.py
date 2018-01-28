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
    assert mission.l10n == {'DictKey_GroupName_102': 'New Vehicle Group #024',
                            'DictKey_GroupName_105': 'New Vehicle Group #025',
                            'DictKey_GroupName_108': 'New Vehicle Group #026',
                            'DictKey_GroupName_111': 'New Vehicle Group #027',
                            'DictKey_GroupName_114': 'New Vehicle Group #028',
                            'DictKey_GroupName_117': 'New Vehicle Group #029',
                            'DictKey_GroupName_12': 'gilles',
                            'DictKey_GroupName_120': 'New Vehicle Group #030',
                            'DictKey_GroupName_123': 'New Vehicle Group #031',
                            'DictKey_GroupName_126': 'New Vehicle Group #032',
                            'DictKey_GroupName_15': 'New Static Object',
                            'DictKey_GroupName_18': 'New Static Object #001',
                            'DictKey_GroupName_21': 'New Static Object #002',
                            'DictKey_GroupName_24': 'New Static Object #003',
                            'DictKey_GroupName_27': 'New Static Object #004',
                            'DictKey_GroupName_30': 'New Vehicle Group',
                            'DictKey_GroupName_33': 'New Vehicle Group #001',
                            'DictKey_GroupName_36': 'New Vehicle Group #002',
                            'DictKey_GroupName_39': 'New Vehicle Group #003',
                            'DictKey_GroupName_42': 'New Vehicle Group #004',
                            'DictKey_GroupName_45': 'New Vehicle Group #005',
                            'DictKey_GroupName_48': 'New Vehicle Group #006',
                            'DictKey_GroupName_51': 'New Vehicle Group #007',
                            'DictKey_GroupName_54': 'New Vehicle Group #008',
                            'DictKey_GroupName_57': 'New Vehicle Group #009',
                            'DictKey_GroupName_6': 'etcher',
                            'DictKey_GroupName_60': 'New Vehicle Group #010',
                            'DictKey_GroupName_63': 'New Vehicle Group #011',
                            'DictKey_GroupName_66': 'New Vehicle Group #012',
                            'DictKey_GroupName_69': 'New Vehicle Group #013',
                            'DictKey_GroupName_72': 'New Vehicle Group #014',
                            'DictKey_GroupName_75': 'New Vehicle Group #015',
                            'DictKey_GroupName_78': 'New Vehicle Group #016',
                            'DictKey_GroupName_81': 'New Vehicle Group #017',
                            'DictKey_GroupName_84': 'New Vehicle Group #018',
                            'DictKey_GroupName_87': 'New Vehicle Group #019',
                            'DictKey_GroupName_9': 'gal',
                            'DictKey_GroupName_90': 'New Vehicle Group #020',
                            'DictKey_GroupName_93': 'New Vehicle Group #021',
                            'DictKey_GroupName_96': 'New Vehicle Group #022',
                            'DictKey_GroupName_99': 'New Vehicle Group #023',
                            'DictKey_UnitName_10': 'gal',
                            'DictKey_UnitName_100': 'Unit #023',
                            'DictKey_UnitName_103': 'Unit #024',
                            'DictKey_UnitName_106': 'Unit #025',
                            'DictKey_UnitName_109': 'Unit #026',
                            'DictKey_UnitName_112': 'Unit #027',
                            'DictKey_UnitName_115': 'Unit #028',
                            'DictKey_UnitName_118': 'Unit #029',
                            'DictKey_UnitName_121': 'Unit #030',
                            'DictKey_UnitName_124': 'Unit #031',
                            'DictKey_UnitName_127': 'Unit #032',
                            'DictKey_UnitName_13': 'gilles',
                            'DictKey_UnitName_16': '',
                            'DictKey_UnitName_19': '',
                            'DictKey_UnitName_22': '',
                            'DictKey_UnitName_25': '',
                            'DictKey_UnitName_28': '',
                            'DictKey_UnitName_31': 'Unit #1',
                            'DictKey_UnitName_34': 'Unit #001',
                            'DictKey_UnitName_37': 'Unit #002',
                            'DictKey_UnitName_40': 'Unit #003',
                            'DictKey_UnitName_43': 'Unit #004',
                            'DictKey_UnitName_46': 'Unit #005',
                            'DictKey_UnitName_49': 'Unit #006',
                            'DictKey_UnitName_52': 'Unit #007',
                            'DictKey_UnitName_55': 'Unit #008',
                            'DictKey_UnitName_58': 'Unit #009',
                            'DictKey_UnitName_61': 'Unit #010',
                            'DictKey_UnitName_64': 'Unit #011',
                            'DictKey_UnitName_67': 'Unit #012',
                            'DictKey_UnitName_7': 'etcher',
                            'DictKey_UnitName_70': 'Unit #013',
                            'DictKey_UnitName_73': 'Unit #014',
                            'DictKey_UnitName_76': 'Unit #015',
                            'DictKey_UnitName_79': 'Unit #016',
                            'DictKey_UnitName_82': 'Unit #017',
                            'DictKey_UnitName_85': 'Unit #018',
                            'DictKey_UnitName_88': 'Unit #019',
                            'DictKey_UnitName_91': 'Unit #020',
                            'DictKey_UnitName_94': 'Unit #021',
                            'DictKey_UnitName_97': 'Unit #022',
                            'DictKey_WptName_101': '',
                            'DictKey_WptName_104': '',
                            'DictKey_WptName_107': '',
                            'DictKey_WptName_11': '',
                            'DictKey_WptName_110': '',
                            'DictKey_WptName_113': '',
                            'DictKey_WptName_116': '',
                            'DictKey_WptName_119': '',
                            'DictKey_WptName_122': '',
                            'DictKey_WptName_125': '',
                            'DictKey_WptName_128': '',
                            'DictKey_WptName_14': '',
                            'DictKey_WptName_17': '',
                            'DictKey_WptName_20': '',
                            'DictKey_WptName_23': '',
                            'DictKey_WptName_26': '',
                            'DictKey_WptName_29': '',
                            'DictKey_WptName_32': '',
                            'DictKey_WptName_35': '',
                            'DictKey_WptName_38': '',
                            'DictKey_WptName_41': '',
                            'DictKey_WptName_44': '',
                            'DictKey_WptName_47': '',
                            'DictKey_WptName_50': '',
                            'DictKey_WptName_53': '',
                            'DictKey_WptName_56': '',
                            'DictKey_WptName_59': '',
                            'DictKey_WptName_62': '',
                            'DictKey_WptName_65': '',
                            'DictKey_WptName_68': '',
                            'DictKey_WptName_71': '',
                            'DictKey_WptName_74': '',
                            'DictKey_WptName_77': '',
                            'DictKey_WptName_8': '',
                            'DictKey_WptName_80': '',
                            'DictKey_WptName_83': '',
                            'DictKey_WptName_86': '',
                            'DictKey_WptName_89': '',
                            'DictKey_WptName_92': '',
                            'DictKey_WptName_95': '',
                            'DictKey_WptName_98': '',
                            'DictKey_descriptionBlueTask_3': '',
                            'DictKey_descriptionNeutralsTask_4': '',
                            'DictKey_descriptionRedTask_2': '',
                            'DictKey_descriptionText_1': '',
                            'DictKey_sortie_5': 'sortie_test'}, pprint.pprint(mission.l10n)


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
    assert mission.next_group_id == 42
    with pytest.raises(IndexError):
        with Miz(duplicate_group_id) as miz:
            assert miz.mission.next_group_id


def test_next_unit_id(mission, duplicate_group_id):
    assert mission.next_unit_id == 42
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
