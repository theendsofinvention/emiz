# coding=utf-8

from pathlib import Path

import pytest
from mockito import verify, verifyStubbedInvocationsAreUsed, when

from emiz.miz import Miz
from emiz.weather import custom_metar, mission_weather
from emiz.weather.mizfile import mizfile_set_metar

_DUMMY_METAR = 'UGTB 210500Z VRB02KT 9999 FEW041 21/15 Q1020 NOSIG'


def test_set_metar(test_file, out_file):
    # when(Miz).zip(...)
    error, result = mizfile_set_metar.set_weather_from_metar(_DUMMY_METAR, test_file, out_file)
    # verifyStubbedInvocationsAreUsed()
    assert f'successfully applied METAR to {test_file}' == result
    with Miz(out_file) as miz:
        assert miz.mission.weather.temperature == 21


def test_no_out_file(test_file):
    when(Miz).zip(...)
    error, result = mizfile_set_metar.set_weather_from_metar(_DUMMY_METAR, test_file)
    verifyStubbedInvocationsAreUsed()
    verify(Miz).zip(str(test_file))
    assert f'successfully applied METAR to {test_file}' == result


def test_error_when_retrieving_metar(test_file):
    when(custom_metar.CustomMetar).get_metar(_DUMMY_METAR).thenReturn(('error', None))
    error, result = mizfile_set_metar.set_weather_from_metar(_DUMMY_METAR, test_file)
    verifyStubbedInvocationsAreUsed()
    assert result is None
    assert 'error' == error


def test_error_when_applying_weather_to_mission(test_file, out_file):
    when(mission_weather.MissionWeather).apply_to_miz(...).thenRaise(ValueError)
    error, result = mizfile_set_metar.set_weather_from_metar(_DUMMY_METAR, test_file, out_file)
    verifyStubbedInvocationsAreUsed()
    assert result is None
    assert 'Unable to apply METAR string to the mission' in error
