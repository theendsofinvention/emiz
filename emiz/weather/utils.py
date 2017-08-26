# coding=utf-8
import json
import logging

import requests
from metar import Metar

from emiz.weather.mission_weather import MissionWeather

LOGGER = logging.getLogger('EMIZ').getChild(__name__)
BASE_TAF_URL = r'http://tgftp.nws.noaa.gov/data/forecasts/taf/stations/{station}.TXT'
BASE_METAR_URL = r'http://tgftp.nws.noaa.gov/data/observations/metar/stations/{station}.TXT'


def _retrieve_taf(station_icao):
    url = BASE_TAF_URL.format(station=station_icao)
    with requests.get(url) as resp:
        if not resp.ok:
            raise FileNotFoundError(f'unable to obtain TAF for station {station_icao} from url: {url}')
        return '\n'.join(resp.content.decode().split('\n')[1:])


def retrieve_metar(station_icao):
    url = BASE_METAR_URL.format(station=station_icao)
    with requests.get(url) as resp:
        if not resp.ok:
            return f'unable to obtain METAR for station {station_icao}\n', None
        f'Got to "http://tgftp.nws.noaa.gov/data/observations/metar/stations" for a list of valid stations'
        return None, resp.content.decode().split('\n')[1]


def set_weather_from_metar_obj(metar: Metar.Metar, in_file, out_file):
    LOGGER.debug(f'METAR: {metar.code}')
    LOGGER.debug(f'applying metar: {in_file} -> {out_file}')
    try:
        if MissionWeather(metar).apply_to_miz(in_file, out_file):
            return None, f'successfully applied METAR to {in_file}'
    except ValueError:
        error = f'Unable to apply METAR string to the mission.\n'
        f'This is most likely due to a freak value, this feature is still experimental.\n'
        f'I will fix it ASAP !'
        return error, None



def set_weather_from_metar_str(metar_str, in_file, out_file):
    error, metar = parse_metar_string(metar_str)
    if error:
        return error, None
    else:
        return set_weather_from_metar_obj(metar, in_file, out_file)


def set_weather_from_icao(station_icao, in_file, out_file):
    LOGGER.debug(f'getting METAR for {station_icao}')
    error, metar_str = retrieve_metar(station_icao)
    if error:
        return error, None
    else:
        return set_weather_from_metar_str(metar_str, in_file, out_file)


def parse_metar_string(metar_string):
    try:
        return None, Metar.Metar(metar_string)
    except Metar.ParserError:
        return f'invalid METAR string: {metar_string}', None