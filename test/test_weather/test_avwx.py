# coding=utf-8

import pytest

from emiz.weather import AVWX, AVWXResult


def test_query_icao_ugtb():
    data = AVWX.query_icao('UGTB')
    assert isinstance(data, AVWXResult)
    assert isinstance(data.altimeter, str)
    assert data.info['Elevation'] == '495'
    assert data.info['City'] == 'Tbilisi'
    assert data.info['Country'] == 'GEO'
    assert data.info['ICAO'] == data.station == 'UGTB'
    assert data.info['Name'] == 'International Airport'

    str_data = ['altimeter', 'dewpoint', 'flightrules', 'rawreport', 'remarks',
                'speech', 'summary', 'temperature', 'time', 'visibility', 'winddirection',
                'windgust', 'windspeed']
    dict_data = ['remarksinfo', 'units']
    list_data = ['windvariabledir', 'otherlist', 'runwayvislist', 'cloudlist']

    for x in str_data:
        assert isinstance(getattr(data, x), str), x

    for x in list_data:
        assert isinstance(getattr(data, x), list), x

    for x in dict_data:
        assert isinstance(getattr(data, x), dict), x


@pytest.mark.parametrize('icao', ['UGTB', 'UGKO', 'KJFK', 'LFPG', 'URSS', 'EBBR'])
def test_query_icao(icao):
    data = AVWX.query_icao(icao)
    assert isinstance(data, AVWXResult)
    assert isinstance(data.altimeter, str)

    str_data = ['altimeter', 'dewpoint', 'flightrules', 'rawreport', 'remarks',
                'speech', 'summary', 'temperature', 'time', 'visibility', 'winddirection',
                'windgust', 'windspeed']
    dict_data = ['remarksinfo', 'units']
    list_data = ['windvariabledir', 'otherlist', 'runwayvislist', 'cloudlist']

    for x in str_data:
        assert isinstance(getattr(data, x), str), x

    for x in list_data:
        assert isinstance(getattr(data, x), list), x

    for x in dict_data:
        assert isinstance(getattr(data, x), dict), x


def test_speech():
    speech = AVWX.metar_to_speech('KJFK 241051Z 35007KT 10SM SCT200 BKN250 03/M02 A3016 RMK AO2 SLP211 T00281017')
    assert 'Winds three five zero at 7kt. Visibility one zero ' \
           'miles. Temperature three degrees Celsius. Dew point minus two degrees Celsius. Q N H three zero ' \
           'point one six. Scattered clouds at 20000ft. Broken layer at 25000ft' == speech
