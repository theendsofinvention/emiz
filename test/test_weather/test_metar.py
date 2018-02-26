# coding=utf-8
import random
from pathlib import Path

import elib.path
import pytest
from metar.Metar import Metar

import emiz.weather
from emiz import Miz
from emiz.mission import Mission


@pytest.fixture(name='bogus_cloud_atl_test_file')
def _bogus_cloud_atl_test_file(test_files_folder):
    yield Path(test_files_folder, 'TRMT_5.1.0-OVC-171220.miz')


def _randomize_weather(mission: Mission):
    mission.weather.qnh = random.randint(720, 790)
    try:
        mission.weather.precipitations = random.randint(0, 4)
    except ValueError:
        pass
    mission.weather.wind_at_ground_level_speed = random.randint(0, 50)
    mission.weather.wind_at2000_speed = random.randint(0, 50)
    mission.weather.wind_at8000_speed = random.randint(0, 50)
    mission.weather.wind_at_ground_level_dir = random.randint(0, 359)
    mission.weather.wind_at2000_dir = random.randint(0, 359)
    mission.weather.wind_at8000_dir = random.randint(0, 359)


@pytest.mark.parametrize('icao', ['UGTB', 'UGTO', 'UGKO', 'UGSA', 'UGDT', 'URSS', 'EBBR'])
def test_set_weather_from_icao(icao, weather_test_file, out_file):
    result = emiz.weather.mizfile.set_weather_from_metar(icao, weather_test_file, out_file)
    assert isinstance(result, tuple)
    assert result[0] is None
    with Miz(weather_test_file) as miz:
        miz._encode()
        m1 = miz.mission
    with Miz(out_file) as miz:
        miz._encode()
        m2 = miz.mission
    for (coa1, coa2) in ((m1._red_coa, m2._red_coa), (m1._blue_coa, m2._blue_coa)):
        for attr in ('_section_bullseye', '_section_coalition', '_section_country', '_section_nav_points'):
            assert getattr(coa1, attr) == getattr(coa2, attr)
    assert m1.weather != m2.weather


@pytest.mark.parametrize('metar,out', [
    ('UGTB 211300Z 13014KT CAVOK 33/07 Q1016 R13R/CLRD70 NOSIG',
     {'visibility': 10000, 'cloud_thickness': 200, 'atmosphere_type': 0,
      'cloud_base': 300, 'cloud_density': 0, 'turbulence_at_ground_level': 0,
      'wind_at_ground_level_speed': 7, 'precipitations': 0, 'qnh': 762}),
    ('UGTB 220830Z 31017KT CAVOK 11/02 Q1012 R31L/CLRD70 NOSIG',
     {'visibility': 10000, 'cloud_thickness': 200, 'atmosphere_type': 0,
      'cloud_base': 300, 'cloud_density': 0, 'turbulence_at_ground_level': 0,
      'wind_at_ground_level_speed': 8, 'precipitations': 0, 'qnh': 759}),
    ('UGTB 230820Z 09009KT 060V120 CAVOK M03/M12 Q1022 NOSIG',
     {'visibility': 10000, 'cloud_thickness': 200, 'atmosphere_type': 0,
      'cloud_base': 300, 'cloud_density': 0, 'turbulence_at_ground_level': 0,
      'wind_at_ground_level_speed': 4, 'precipitations': 0, 'qnh': 766}),
    ('UGTB 240930Z 00000MPS 8000 -SHRA BKN009 OVC050CB 08/06 Q1014 R06/290055 NOSIG RMK R02/00000MPS MT OBSC QFE759',
     {'visibility': 8000, 'cloud_thickness': (1800, 2000), 'atmosphere_type': 0,
      'cloud_base': 1523, 'cloud_density': (9, 10), 'turbulence_at_ground_level': 0,
      'wind_at_ground_level_speed': 0, 'precipitations': 1, 'qnh': 760}),
    ('ENGM 240850Z 16003KT 9999 -SN FEW014 OVC028 M07/M09 Q1038 TEMPO BKN014',
     {'visibility': 10000, 'cloud_thickness': (1800, 2000), 'atmosphere_type': 0,
      'cloud_base': 853, 'cloud_density': (9, 10), 'turbulence_at_ground_level': 0,
      'wind_at_ground_level_speed': 1, 'precipitations': 3, 'qnh': 778}),
])
def test_set_weather_from_metar(metar, out, weather_test_file, out_file):
    in_metar = Metar(metar)
    with Miz(weather_test_file) as miz:
        _randomize_weather(miz.mission)
        miz.zip(out_file)
    emiz.weather.mizfile.set_weather_from_metar(metar, out_file, out_file)
    out_metar = Metar(emiz.weather.mizfile.get_metar_from_mission(out_file, 'UGTB'))
    assert in_metar.temp.value() == out_metar.temp.value()
    assert int(in_metar.wind_speed.value('MPS')) == out_metar.wind_speed.value('MPS')
    assert in_metar.wind_dir.value() == out_metar.wind_dir.value()
    with Miz(out_file) as miz:
        assert miz.mission.weather.wind_at_ground_level_dir == emiz.weather.utils.reverse_direction(
            in_metar.wind_dir.value())
        assert miz.mission.weather.wind_at2000_speed >= miz.mission.weather.wind_at_ground_level_speed
        assert miz.mission.weather.wind_at8000_speed >= miz.mission.weather.wind_at_ground_level_speed
        for key in out:
            if isinstance(out[key], tuple):
                assert out[key][0] <= getattr(miz.mission.weather, key) <= out[key][1]
            else:
                assert getattr(miz.mission.weather, key) == out[key], key


@pytest.mark.long
def test_bogus_cloud_alt(bogus_cloud_atl_test_file):
    base = int(round(1400 * 3.28084, -2))
    assert base == 4600
    assert f'{base:04}' == '4600'
    metar = emiz.weather.mizfile.get_metar_from_mission(bogus_cloud_atl_test_file)
    assert '02104MPS 9999M OVC046 07/07 Q1028 NOSIG' in metar
    metar = emiz.weather.custom_metar.CustomMetar(metar)
    assert 'sky: overcast at 4600 feet' in metar.string()
