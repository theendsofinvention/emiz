# coding=utf-8

import os

import pytest
from metar.Metar import Metar

from emiz import Miz
from emiz.weather import build_metar_from_mission, set_weather_from_icao
from emiz.weather.utils import set_weather_from_metar_str

TEST_FILE_PATH = './test/test_files'
if not os.path.exists(TEST_FILE_PATH):
    raise RuntimeError(f'cannot find test files in: {TEST_FILE_PATH}')
BASE_PATH = os.path.abspath(TEST_FILE_PATH)

TEST_FILE = os.path.join(BASE_PATH, 'weather.miz')
OUT_FILE = os.path.join(BASE_PATH, 'weather_output.miz')


@pytest.mark.parametrize('icao', ['UGTB', 'UGTO', 'UGKO', 'UGSA', 'UGDT', 'URSS', 'EBBR'])
def test_set_weather_from_icao(icao):
    result = set_weather_from_icao(icao, TEST_FILE, OUT_FILE)
    assert isinstance(result, tuple)
    assert result[0] is None
    with Miz(TEST_FILE) as miz:
        miz._encode()
        m1 = miz.mission
    with Miz(OUT_FILE) as miz:
        miz._encode()
        m2 = miz.mission
    for (coa1, coa2) in ((m1.red_coa, m2.red_coa), (m1.blue_coa, m2.blue_coa)):
        for attr in ('_section_bullseye', '_section_coalition', '_section_country', '_section_nav_points'):
            assert getattr(coa1, attr) == getattr(coa2, attr)
    assert m1.weather != m2.weather


@pytest.mark.parametrize('metar', [
    'UGTB 201300Z 13014KT CAVOK 33/07 Q1016 R13R/CLRD70 NOSIG',
])
def test_set_weather_from_metar(metar):
    in_metar = Metar(metar)
    set_weather_from_metar_str(metar, TEST_FILE, OUT_FILE)
    out_metar = Metar(build_metar_from_mission(OUT_FILE, 'UGTB'))
    assert in_metar.temp.value() == out_metar.temp.value()
    assert int(in_metar.wind_speed.value('MPS')) == out_metar.wind_speed.value('MPS')
    assert in_metar.wind_dir.value() == out_metar.wind_dir.value()
