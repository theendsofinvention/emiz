# coding=utf-8


import json
import logging

import requests
from metar.Metar import Metar
from .mission_weather import MissionWeather, build_metar_from_mission

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
            raise FileNotFoundError(f'unable to obtain METAR for station {station_icao} from url: {url}')
        return resp.content.decode().split('\n')[1]


def set_weather_from_metar_str(metar_str, in_file, out_file):
    result = {
        'metar': metar_str,
        'from': in_file,
        'to': out_file,
    }
    try:
        metar = Metar(metar_str)
        result['icao'] = metar.station_id
    except:
        LOGGER.error('Failed to parse METAR string. This is a bug in the METAR library, I will take a look ASAP')
        result['status'] = 'failed'
    else:
        LOGGER.debug(f'METAR: {metar.code}')
        LOGGER.debug(f'applying metar: {in_file} -> {out_file}')
        try:
            if MissionWeather(metar).apply_to_miz(in_file, out_file):
                result['status'] = 'success'
        except ValueError:
            result['status'] = 'failed'
            result['error'] = f'Unable to apply METAR string to the mission.\n'
            f'This is most likely due to a freak value, this feature is still experimental.\n'
            f'I will fix it ASAP !'
    finally:
        return result


def set_weather_from_icao(station_icao, in_file, out_file):
    LOGGER.debug(f'getting METAR for {station_icao}')
    result = {
        'icao': station_icao,
        'from': in_file,
        'to': out_file,
    }
    try:
        metar_str = retrieve_metar(station_icao)
    except FileNotFoundError:
        result['status'] = 'failed'
        result['error'] = f'unable to obtain METAR for station {station_icao}\n'
        f'Got to "http://tgftp.nws.noaa.gov/data/observations/metar/stations" for a list of valid stations'
    else:
        result = set_weather_from_metar_str(metar_str, in_file, out_file)
    return json.dumps(result)