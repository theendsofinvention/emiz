# coding=utf-8
from mockito import verifyStubbedInvocationsAreUsed, when

import emiz.mission_time
import emiz.weather
from emiz.edit_miz import edit_miz
from emiz.miz import Miz
from emiz.new_miz import NewMiz

METAR = 'UGTB 240830Z 31017KT CAVOK 11/02 Q1012 R31L/CLRD70 NOSIG'
TIME = '20180201225000'


def test_time(test_file, out_file):
    result = edit_miz(test_file, out_file, time=TIME)
    assert not result
    with NewMiz(out_file) as miz:
        assert miz.mission.mission_start_time_as_string == '22:50:00'
        assert miz.mission.mission_start_date_as_string == '01/02/2018'


def test_weather(test_file, out_file):
    result = edit_miz(test_file, out_file, metar=METAR)
    assert not result
    with NewMiz(out_file) as miz:
        assert miz.mission.weather.wind_at_ground_level_dir == 130
        assert miz.mission.weather.wind_at_ground_level_speed == 8
        assert miz.mission.weather.cloud_base == 300
        assert miz.mission.weather.cloud_density == 0
        assert miz.mission.weather.qnh == 759
        assert miz.mission.weather.precipitations == 0


def test_no_outfile(caplog, out_file):
    edit_miz(out_file)
    assert 'editing in place' in caplog.text


def test_nothing_to_do(out_file):
    assert edit_miz(out_file) == 'nothing to do!'


def test_metar_error(out_file):
    when(emiz.weather.custom_metar.CustomMetar).get_metar(...).thenReturn(('error', None))
    assert edit_miz(out_file, metar='plop') == 'error'
    verifyStubbedInvocationsAreUsed()


def test_bad_time_string(out_file):
    assert edit_miz(out_file, time='plop') == 'badly formatted time string: plop'


def test_apply_metar_failed(test_file, out_file):
    when(emiz.weather.mission_weather.MissionWeather).apply_to_miz(...).thenReturn(False)
    assert edit_miz(test_file, out_file, metar=METAR) == 'error while applying METAR to mission'
    verifyStubbedInvocationsAreUsed()


def test_apply_time_failed(test_file, out_file):
    when(emiz.mission_time.MissionTime).apply_to_miz(...).thenReturn(False)
    assert edit_miz(test_file, out_file, time=TIME) == 'error while setting time on mission'
    verifyStubbedInvocationsAreUsed()


def test_zip_error(test_file, out_file):
    when(Miz).zip(...).thenRaise(OSError)
    assert edit_miz(test_file, out_file, time=TIME) == \
        f'permission error: cannot edit "{out_file}"; maybe it is in use ?'
    verifyStubbedInvocationsAreUsed()
