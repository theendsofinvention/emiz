# coding=utf-8

import random

import elib.path
import pytest
from metar.Metar import Metar

import emiz.weather
from emiz import Miz
from emiz.mission import Mission

TEST_FILES_FOLDER = elib.path.ensure_path('./test/test_files').absolute()
if not TEST_FILES_FOLDER.exists():
    raise RuntimeError(f'cannot find test files in: {str(TEST_FILES_FOLDER.absolute())}')

TEST_FILE = TEST_FILES_FOLDER.joinpath('weather.miz')
OUT_FILE = TEST_FILES_FOLDER.joinpath('weather_output.miz')
BOGUS_CLOUD_ALT_TEST_FILE = TEST_FILES_FOLDER.joinpath('TRMT_5.1.0-OVC-171220.miz')


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
def test_set_weather_from_icao(icao):
    result = emiz.weather.mizfile.set_weather_from_metar(icao, TEST_FILE, OUT_FILE)
    assert isinstance(result, tuple)
    assert result[0] is None
    with Miz(TEST_FILE) as miz:
        miz._encode()
        m1 = miz.mission
    with Miz(OUT_FILE) as miz:
        miz._encode()
        m2 = miz.mission
    for (coa1, coa2) in ((m1._red_coa, m2._red_coa), (m1._blue_coa, m2._blue_coa)):
        for attr in ('_section_bullseye', '_section_coalition', '_section_country', '_section_nav_points'):
            assert getattr(coa1, attr) == getattr(coa2, attr)
    assert m1.weather != m2.weather


@pytest.mark.parametrize('metar', [
    'UGTB 201300Z 13014KT CAVOK 33/07 Q1016 R13R/CLRD70 NOSIG',
])
def test_set_weather_from_metar(metar):
    in_metar = Metar(metar)
    random_file = elib.path.ensure_path('./test.miz', must_exist=False)
    with Miz(TEST_FILE) as miz:
        _randomize_weather(miz.mission)
        miz.zip(random_file)
    emiz.weather.mizfile.set_weather_from_metar(metar, random_file, OUT_FILE)
    out_metar = Metar(emiz.weather.mizfile.get_metar_from_mission(OUT_FILE, 'UGTB'))
    assert in_metar.temp.value() == out_metar.temp.value()
    assert int(in_metar.wind_speed.value('MPS')) == out_metar.wind_speed.value('MPS')
    assert in_metar.wind_dir.value() == out_metar.wind_dir.value()
    assert out_metar.temp.value() == 33.0
    assert out_metar.wind_dir.value() == 130
    assert out_metar.wind_speed.value() == 7.0
    with Miz(OUT_FILE) as miz:
        assert miz.mission.weather.wind_at_ground_level_dir == emiz.weather.utils.reverse_direction(
            in_metar.wind_dir.value())
        assert miz.mission.weather.visibility == 10000
        assert miz.mission.weather.cloud_thickness == 200
        assert miz.mission.weather.atmosphere_type == 0
        assert miz.mission.weather.cloud_base == 300
        assert miz.mission.weather.cloud_density == 0
        assert miz.mission.weather.turbulence_at_ground_level == 0
        assert miz.mission.weather.wind_at_ground_level_speed == 7
        assert miz.mission.weather.wind_at_ground_level_dir == 310
        assert miz.mission.weather.wind_at2000_speed >= miz.mission.weather.wind_at_ground_level_speed
        assert miz.mission.weather.wind_at8000_speed >= miz.mission.weather.wind_at2000_speed
        assert miz.mission.weather.precipitations == 0
        assert miz.mission.weather.qnh == 762


@pytest.mark.long
def test_bogus_cloud_alt():
    base = int(round(1400 * 3.28084, -2))
    assert base == 4600
    assert f'{base:04}' == '4600'
    metar = emiz.weather.mizfile.get_metar_from_mission(BOGUS_CLOUD_ALT_TEST_FILE)
    assert '02104MPS 9999M OVC046 07/07 Q1028 NOSIG' in metar
    metar = emiz.weather.custom_metar.CustomMetar(metar)
    assert 'sky: overcast at 4600 feet' in metar.string()
