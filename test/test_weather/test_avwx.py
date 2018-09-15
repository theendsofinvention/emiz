# coding=utf-8

import pytest

from emiz.weather import AVWX, AVWXResult

_STR_DATA = ['altimeter', 'dewpoint', 'flightrules', 'rawreport', 'remarks',
             'speech', 'summary', 'temperature', 'time', 'visibility', 'winddirection',
             'windgust', 'windspeed']
_DICT_DATA = ['remarksinfo', 'units']
_LIST_DATA = ['windvariabledir', 'otherlist', 'runwayvislist', 'cloudlist']


def _check_data(data):

    for x in _STR_DATA:
        assert isinstance(getattr(data, x), str), x

    for x in _LIST_DATA:
        assert isinstance(getattr(data, x), list), x

    for x in _DICT_DATA:
        assert isinstance(getattr(data, x), dict), x


@pytest.mark.vcr()
def test_query_icao_ugtb():
    data = AVWX.query_icao('UGTB')
    assert isinstance(data, AVWXResult)
    assert isinstance(data.altimeter, str)
    assert data.info['Elevation'] == 495.0
    assert data.info['City'] == 'Tbilisi'
    assert data.info['Country'] == 'GEO'
    assert data.info['Icao'] == data.station == 'UGTB'
    assert data.info['Name'] == 'International Airport'
    _check_data(data)


@pytest.mark.vcr()
@pytest.mark.parametrize('icao', ['UGTB', 'UGKO', 'KJFK', 'LFPG', 'URSS', 'EBBR'])
# @pytest.mark.parametrize('icao', ['UGTB', 'UGKO', 'LFPG'])
def test_query_icao(icao):
    data = AVWX.query_icao(icao)
    assert isinstance(data, AVWXResult)
    assert isinstance(data.altimeter, str)
    _check_data(data)


@pytest.mark.vcr()
def test_speech():
    speech = AVWX.metar_to_speech('KJFK 241051Z 35007KT 10SM SCT200 BKN250 03/M02 A3016 RMK AO2 SLP211 T00281017')
    assert 'Winds three five zero at 7kt. Visibility one zero ' \
           'miles. Temperature three degrees Celsius. Dew point minus two degrees Celsius. Q N H three zero ' \
           'point one six. Scattered clouds at 20000ft. Broken layer at 25000ft' == speech
