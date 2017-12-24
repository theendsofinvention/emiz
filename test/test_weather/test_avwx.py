# coding=utf-8

import pytest

from emiz.weather import AVWX, AVWXResult


def test_query_icao_ugtb():
    data = AVWX.query_icao('UGTB')
    assert isinstance(data, AVWXResult)
    assert isinstance(data.Altimeter, str)
    assert data.Elevation == '495'
    assert data.City == 'Tbilisi'
    assert data.Country == 'GEO'
    assert data.ICAO == data.Station == 'UGTB'
    assert data.Name == 'International Airport'

    str_data = ['Altimeter', 'Dewpoint', 'FlightRules', 'RawReport', 'Remarks',
                'Speech', 'Summary', 'Temperature', 'Time', 'Visibility', 'WindDirection',
                'WindGust', 'WindSpeed']
    dict_data = ['RemarksInfo', 'Units']
    list_data = ['WindVariableDir', 'OtherList', 'RunwayVisList', 'CloudList']

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
    assert isinstance(data.Altimeter, str)

    str_data = ['Altimeter', 'Dewpoint', 'FlightRules', 'RawReport', 'Remarks',
                'Speech', 'Summary', 'Temperature', 'Time', 'Visibility', 'WindDirection',
                'WindGust', 'WindSpeed']
    dict_data = ['RemarksInfo', 'Units']
    list_data = ['WindVariableDir', 'OtherList', 'RunwayVisList', 'CloudList']

    for x in str_data:
        assert isinstance(getattr(data, x), str), x

    for x in list_data:
        assert isinstance(getattr(data, x), list), x

    for x in dict_data:
        assert isinstance(getattr(data, x), dict), x
