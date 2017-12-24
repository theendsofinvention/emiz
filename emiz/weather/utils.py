# coding=utf-8
"""
Utility function for weather
"""
import re
import typing

import requests
from metar import Metar

from emiz import MAIN_LOGGER
from emiz.miz import Miz
from emiz.weather.custom_metar import CustomMetar
from emiz.weather.mission_weather import MissionWeather

LOGGER = MAIN_LOGGER.getChild(__name__)
BASE_TAF_URL = r'http://tgftp.nws.noaa.gov/data/forecasts/taf/stations/{station}.TXT'
BASE_METAR_URL = r'http://tgftp.nws.noaa.gov/data/observations/metar/stations/{station}.TXT'


def _retrieve_taf(station_icao):
    url = BASE_TAF_URL.format(station=station_icao)
    with requests.get(url) as resp:
        if not resp.ok:
            raise FileNotFoundError(f'unable to obtain TAF for station {station_icao} from url: {url}')
        return '\n'.join(resp.content.decode().split('\n')[1:])


def retrieve_metar(station_icao) \
        -> typing.Tuple[typing.Union[str, None], typing.Union[str, None]]:
    """
    Retrieves a METAR string from an online database

    Args:
        station_icao: ICAO of the station

    Returns: tuple of error, metar_str

    """
    url = BASE_METAR_URL.format(station=station_icao)
    with requests.get(url) as resp:
        if not resp.ok:
            return f'unable to obtain METAR for station {station_icao}\n' \
                   f'Got to "http://tgftp.nws.noaa.gov/data/observations/metar/stations" ' \
                   f'for a list of valid stations', None
        return None, resp.content.decode().split('\n')[1]


def set_weather_from_metar_obj(metar: Metar.Metar, in_file, out_file=None) \
        -> typing.Tuple[typing.Union[str, None], typing.Union[str, None]]:
    """
    Applies the weather from a METAR object to a MIZ file

    Args:
        metar: metar object
        in_file: path to MIZ file
        out_file: path to output MIZ file (will default to in_file)

    Returns: tuple of error, success

    """
    if out_file is None:
        out_file = in_file
    LOGGER.debug(f'METAR: {metar.code}')
    LOGGER.debug(f'applying metar: {in_file} -> {out_file}')
    try:
        with Miz(in_file) as miz:
            MissionWeather(metar).apply_to_miz(miz)
            miz.zip(out_file)
            return None, f'successfully applied METAR to {in_file}'
    except ValueError:
        error = f'Unable to apply METAR string to the mission.\n' \
                f'This is most likely due to a freak value, this feature is still experimental.\n' \
                f'I will fix it ASAP !'
        return error, None


def set_weather_from_metar_str(metar_str, in_file, out_file) \
        -> typing.Tuple[typing.Union[str, None], typing.Union[str, None]]:
    """
    Sets the weather for a MIZ file

    Args:
        metar_str: metar string
        in_file: path to MIZ file
        out_file: path to output MIZ file (will default to in_file)

    Returns: tuple of error, success

    """
    error, metar = parse_metar_string(metar_str)
    if error:
        return error, None

    return set_weather_from_metar_obj(metar, in_file, out_file)


def set_weather_from_icao(station_icao, in_file, out_file)\
        -> typing.Tuple[typing.Union[None, str], typing.Union[None, str]]:
    """
    Gets a metar string from the ICAO code and applies it to a MIZ file

    Args:
        station_icao: ICAO code
        in_file: base file
        out_file: output file

    Returns: error, result

    """
    LOGGER.debug(f'getting METAR for {station_icao}')
    error, metar_str = retrieve_metar(station_icao)
    if error:
        return error, None

    return set_weather_from_metar_str(metar_str, in_file, out_file)


def parse_metar_string(metar_string) -> typing.Tuple[typing.Union[None, str], typing.Union[None, Metar.Metar]]:
    """
    Parses a METAR string and return a METAR object
    Args:
        metar_string: string to parse

    Returns: tuple of error, metar

    """
    metar_string = re.sub(r' CLR[\d]+ ', ' ', metar_string)
    try:
        return None, CustomMetar(metar_string)
    except Metar.ParserError:
        return f'invalid METAR string: {metar_string}', None
