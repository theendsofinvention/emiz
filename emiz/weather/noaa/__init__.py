# coding=utf-8
"""
Query METAR and TAF information from http://tgftp.nws.noaa.gov
"""
import typing

import requests

_BASE_TAF_URL = r'http://tgftp.nws.noaa.gov/data/forecasts/taf/stations/{station}.TXT'
_BASE_METAR_URL = r'http://tgftp.nws.noaa.gov/data/observations/metar/stations/{station}.TXT'


def retrieve_taf(station_icao) -> typing.Tuple[typing.Union[str, None], typing.Union[str, None]]:
    """
    Retrieves a TAF string from an online database

    Args:
        station_icao: ICAO of the station

    Returns:
        tuple of error, metar_str
    """
    url = _BASE_TAF_URL.format(station=station_icao)
    with requests.get(url) as resp:
        if not resp.ok:
            return f'unable to obtain TAF for station {station_icao}\n' \
                   f'Got to "http://tgftp.nws.noaa.gov/data/observations/metar/stations" ' \
                   f'for a list of valid stations', None
        return None, resp.content.decode().split('\n')[1]


def retrieve_metar(station_icao) -> typing.Tuple[typing.Union[str, None], typing.Union[str, None]]:
    """
    Retrieves a METAR string from an online database

    Args:
        station_icao: ICAO of the station

    Returns:
        tuple of error, metar_str
    """
    url = _BASE_METAR_URL.format(station=station_icao)
    with requests.get(url) as resp:
        if not resp.ok:
            return f'unable to obtain METAR for station {station_icao}\n' \
                   f'Got to "http://tgftp.nws.noaa.gov/data/observations/metar/stations" ' \
                   f'for a list of valid stations', None
        return None, resp.content.decode().split('\n')[1]
