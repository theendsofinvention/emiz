# coding=utf-8

import logging

from metar.Metar import Metar
from emiz.miz import Miz
from emiz.weather import MissionWeather, parse_metar_string, retrieve_metar
from emiz.mission_time import MissionTime

LOGGER = logging.getLogger('EMIZ').getChild(__name__)


def edit_miz(infile: str, outfile: str = None, metar=None, time=None,
             min_wind=0, max_wind=40):

    if outfile is None:
        LOGGER.debug(f'editing in place: {infile}')
        outfile = infile
    else:
        LOGGER.debug(f'editing miz file: {infile} -> {outfile}')

    if metar:
        if isinstance(metar, str):
            if len(metar) == 4:
                LOGGER.debug('making METAR out of ICAO code')
                metar = parse_metar_string(retrieve_metar(metar))
            else:
                LOGGER.debug('making METAR out of string')
                metar = parse_metar_string(metar)
        if not isinstance(metar, Metar):
            raise RuntimeError(f'not a METAR object: {type(metar)}')
        metar = MissionWeather(metar, min_wind=min_wind, max_wind=max_wind)

    if time:
        try:
            time = MissionTime.from_string(time)
        except ValueError:
            return f'badly formatted time string: {time}'

    if not metar and not time:
        return 'nothing to do!'

    with Miz(infile) as miz:
        if metar:
            if not metar.apply_to_miz(miz):
                return 'error while applying METAR to mission'
        if time:
            if not time.apply_to_miz(miz):
                return 'error while setting time on mission'
        miz.zip(outfile)

