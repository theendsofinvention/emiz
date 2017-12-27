# coding=utf-8
"""
Tests Mission weather
"""
import pytest


def test_qnh(mission):
    assert mission.weather.qnh == 760
    mission.weather.qnh = 754
    assert mission.weather.qnh == 754
    for wrong_qnh in ['caribou', 719, 791, -1, None, True]:
        with pytest.raises(ValueError):
            mission.weather.qnh = wrong_qnh


def test_seasons(mission):
    # Season code has been deprecated by ED
    mission.weather.season_code = mission.weather.seasons_enum['winter']
    mission.weather.temperature = -50
    assert mission.weather.temperature == -50
    mission.weather.season_code = mission.weather.seasons_enum['summer']
    assert mission.weather.temperature == 5
    # with pytest.raises(ValueError):
    mission.weather.temperature = -50
    mission.weather.temperature = 50
    assert mission.weather.temperature == 50
    mission.weather.season_code = mission.weather.seasons_enum['winter']
    assert mission.weather.temperature == 15
    # with pytest.raises(ValueError):
    mission.weather.temperature = 50
    mission.weather.temperature = -50
    mission.weather.season_code = mission.weather.seasons_enum['fall']
    assert mission.weather.temperature == -10
    mission.weather.season_code = mission.weather.seasons_enum['summer']
    assert mission.weather.temperature == 5
    mission.weather.temperature = 50
    mission.weather.season_code = mission.weather.seasons_enum['spring']
    assert mission.weather.temperature == 30
    for test in [(1, 'summer'), (2, 'winter'), (3, 'spring'), (4, 'fall')]:
        assert test[0] == mission.weather.get_season_code_from_name(test[1])
        mission.weather.season_code = test[0]
        assert mission.weather.season_name == test[1]
    for wrong_name in (1, -1, None, True, 'caribou'):
        with pytest.raises(ValueError, msg=wrong_name):
            mission.weather.get_season_code_from_name(wrong_name)


def test_wind(mission):
    assert mission.weather.wind_at2000_dir == 0
    assert mission.weather.wind_at2000_speed == 0
    assert mission.weather.wind_at8000_dir == 0
    assert mission.weather.wind_at8000_speed == 0
    assert mission.weather.wind_at_ground_level_dir == 0
    assert mission.weather.wind_at_ground_level_speed == 0
    for wrong_speed in [-1, 51, True, None, 'caribou']:
        with pytest.raises(ValueError, msg=wrong_speed):
            mission.weather.wind_at_ground_level_speed = wrong_speed
        with pytest.raises(ValueError, msg=wrong_speed):
            mission.weather.wind_at8000_speed = wrong_speed
        with pytest.raises(ValueError, msg=wrong_speed):
            mission.weather.wind_at2000_speed = wrong_speed
    for wrong_dir in [-1, 360, True, None, 'caribou']:
        with pytest.raises(ValueError, msg=wrong_dir):
            mission.weather.wind_at_ground_level_dir = wrong_dir
        with pytest.raises(ValueError, msg=wrong_dir):
            mission.weather.wind_at2000_dir = wrong_dir
        with pytest.raises(ValueError, msg=wrong_dir):
            mission.weather.wind_at8000_dir = wrong_dir
    for i in range(0, 359, 1):
        mission.weather.wind_at8000_dir = i
        mission.weather.wind_at2000_dir = i
        mission.weather.wind_at_ground_level_dir = i
    for i in range(0, 50, 1):
        mission.weather.wind_at8000_speed = i
        mission.weather.wind_at2000_speed = i
        mission.weather.wind_at_ground_level_speed = i


def test_turbulence(mission):
    assert mission.weather.turbulence_at_ground_level == 0
    for i in range(0, 60, 1):
        mission.weather.turbulence_at_ground_level = i
    for wrong_turbulence in [-1, 61, True, None, 'caribou']:
        with pytest.raises(ValueError, msg=wrong_turbulence):
            mission.weather.turbulence_at_ground_level = wrong_turbulence


def test_atmosphere_type(mission):
    assert mission.weather.atmosphere_type == 0
    mission.weather.atmosphere_type = 1
    assert mission.weather.atmosphere_type == 1
    for wrong_atmo_type in [-1, 2, True, None, 'caribou']:
        with pytest.raises(ValueError, msg=wrong_atmo_type):
            mission.weather.atmosphere_type = wrong_atmo_type


def test_fog(mission):
    assert not mission.weather.fog_enabled
    mission.weather.fog_enabled = True
    assert mission.weather.fog_enabled
    assert mission.weather.fog_visibility == 25
    assert mission.weather.fog_thickness == 0
    mission.weather.fog_visibility = 500
    assert mission.weather.fog_visibility == 500
    mission.weather.fog_thickness = 500
    assert mission.weather.fog_thickness == 500
    for i in range(0, 6000, 100):
        mission.weather.fog_visibility = i
    for i in range(0, 1000, 10):
        mission.weather.fog_thickness = i
    for wrong_visibility in [-1, 6001, True, None, 'caribou']:
        with pytest.raises(ValueError, msg=wrong_visibility):
            mission.weather.fog_visibility = wrong_visibility
    for wrong_thickness in [-1, 1001, True, None, 'caribou']:
        with pytest.raises(ValueError, msg=wrong_thickness):
            mission.weather.fog_thickness = wrong_thickness


def test_clouds(mission):
    assert mission.weather.cloud_thickness == 200
    assert mission.weather.cloud_base == 300
    for i in range(0, 10):
        mission.weather.cloud_density = i
    for wrong_density in [-1, 11, True, None, 'caribou']:
        with pytest.raises(ValueError, msg=wrong_density):
            mission.weather.cloud_density = wrong_density
    for i in range(300, 5000, 100):
        mission.weather.cloud_base = i
    for wrong_base in [-1, -500, 5001, 50000, None, False, 'caribou']:
        with pytest.raises(ValueError):
            mission.weather.cloud_base = wrong_base
    for i in range(200, 2000, 50):
        mission.weather.cloud_thickness = i
    for wrong_thickness in [199, 2001, -500, 2, 12000, None, False, 'caribou']:
        with pytest.raises(ValueError):
            mission.weather.cloud_thickness = wrong_thickness


def test_precipitations(mission):
    mission.weather.cloud_density = 4
    mission.weather.season_code = 3
    mission.weather.temperature = 1
    mission.weather.precipitations = 0
    for i in range(1, 4):
        with pytest.raises(ValueError, msg=i):
            mission.weather.precipitations = i
    mission.weather.cloud_density = 5
    mission.weather.precipitations = 1
    for i in range(2, 4):
        with pytest.raises(ValueError, msg=i):
            mission.weather.precipitations = i
    mission.weather.cloud_density = 9
    for i in range(0, 2):
        mission.weather.precipitations = i
    mission.weather.temperature = 0
    for i in range(0, 4):
        mission.weather.precipitations = i
    mission.weather.temperature = -1
    for i in range(3, 4):
        mission.weather.precipitations = i
    for i in range(1, 2):
        with pytest.raises(ValueError, msg=i):
            mission.weather.precipitations = i
    mission.weather.precipitations = 4
    # Season code has been deprecated by ED
    # miz.mission.weather.season_code = 1
    # assert miz.mission.weather.temperature == 5
    # assert miz.mission.weather.precipitations == 2
    # miz.mission.weather.season_code = 2
    # miz.mission.weather.temperature = -20
    # assert miz.mission.weather.precipitations == 4
    # miz.mission.weather.precipitations = 3
    # miz.mission.weather.season_code = 1
    # assert miz.mission.weather.precipitations == 1
