# coding=utf-8

import tempfile
from datetime import datetime

import elib.path
import pytest
from mockito import mock, when

import emiz.miz
from emiz.miz import Mission
from emiz.weather.mizfile.mizfile_get_metar import get_metar_from_mission


@pytest.fixture(name='setup')
def _setup():
    miz = mock()
    mission = mock(spec=Mission)
    mission.weather = mock()
    mission.weather.wind_at_ground_level_dir = 180
    mission.weather.wind_at_ground_level_speed = 0
    mission.weather.visibility = 9999
    mission.weather.fog_visibility = 0
    mission.weather.fog_enabled = False
    mission.weather.precipitations = 0
    mission.weather.cloud_density = 0
    mission.weather.cloud_base = 8000
    mission.weather.temperature = 10
    mission.weather.qnh = 756
    miz.mission = mission
    time = 'time'
    icao = 'UGTB'
    when(emiz.miz.Miz).__enter__(...).thenReturn(miz)
    when(elib.path).ensure_file(...).thenReturn(elib.path.Path('test.miz'))
    when(emiz.miz.Miz).__exit__(...)
    when(tempfile).mkdtemp(...).thenReturn('no_tmp_dir')
    yield miz, mission, time, icao


# http://localhost:63342/EMIZ/htmlcov/emiz_weather_mizfile_mizfile_get_metar_py.html
def test_basic_metar(setup):
    _, _, time, icao = setup
    metar = get_metar_from_mission('test', time=time, icao=icao)
    assert metar == f'{icao} {time} 00000MPS CAVOK 10/10 Q1008 NOSIG'


def test_cavok(setup):
    _, mission, time, icao = setup
    mission.weather.visibility = 9998
    metar = get_metar_from_mission('test', time=time, icao=icao)
    assert 'CAVOK' not in metar


@pytest.mark.parametrize('density', range(0, 10))
def test_cloud_density(setup, density):
    _, mission, time, icao = setup
    mission.weather.cloud_density = density
    metar = get_metar_from_mission('test', time=time, icao=icao)
    if density == 0:
        assert metar == f'{icao} {time} 00000MPS CAVOK 10/10 Q1008 NOSIG'
    elif density < 4:
        assert metar == f'{icao} {time} 00000MPS CAVOK FEW262 10/10 Q1008 NOSIG'
    elif density < 7:
        assert metar == f'{icao} {time} 00000MPS CAVOK SCT262 10/10 Q1008 NOSIG'
    elif density < 9:
        assert metar == f'{icao} {time} 00000MPS CAVOK BKN262 10/10 Q1008 NOSIG'
    else:
        assert metar == f'{icao} {time} 00000MPS CAVOK OVC262 10/10 Q1008 NOSIG'


def test_no_time(setup):
    _, _, _, icao = setup
    now = datetime.utcnow()
    day = now.day
    hour = now.hour
    minute = now.minute
    time = f'{day:02}{hour:02}{minute:02}Z'
    metar = get_metar_from_mission('test', icao=icao)
    assert metar == f'{icao} {time} 00000MPS CAVOK 10/10 Q1008 NOSIG'


@pytest.mark.parametrize('fog_visibility', range(0, 6001, 500))
def test_fog(setup, fog_visibility):
    _, mission, time, icao = setup
    mission.weather.fog_visibility = fog_visibility
    mission.weather.fog_enabled = True
    metar = get_metar_from_mission('test', time=time, icao=icao)
    if fog_visibility < 5000:
        assert metar == f'{icao} {time} 00000MPS {fog_visibility:04d}M 10/10 Q1008 NOSIG'
    else:
        assert metar == f'{icao} {time} 00000MPS {fog_visibility:04d}M 10/10 Q1008 NOSIG'
