# coding=utf-8
"""
Allow for batch edit of time and weather of single miz
"""

import typing

from metar.Metar import Metar

import emiz.weather
from emiz import MAIN_LOGGER
from emiz.mission_time import MissionTime
from emiz.miz import Miz

LOGGER = MAIN_LOGGER.getChild(__name__)


def edit_miz(  # noqa: C901 pylint: disable=too-many-arguments,too-many-branches
        infile: str,
        outfile: str = None,
        metar: typing.Union[str, Metar] = None,
        time: str = None,
        min_wind: int = 0,
        max_wind: int = 40
) -> str:
    # noinspection SpellCheckingInspection
    """
    Edit an opened MIZ file and sets the time and date and the weather

    Args:
        infile: source file
        outfile: output file (will default to source file)
        metar: metar string, ICAO or object to apply
        time: time string to apply (YYYYMMDDHHMMSS)
        min_wind: minimum wind
        max_wind: maximum wind

    Returns:
        String containing error
    """
    if outfile is None:
        LOGGER.debug(f'editing in place: {infile}')
        outfile = infile
    else:
        LOGGER.debug(f'editing miz file: {infile} -> {outfile}')

    mission_weather = None

    if metar:
        error, metar = emiz.weather.custom_metar.CustomMetar(metar)
        if error:
            return error

        mission_weather = emiz.weather.mission_weather.MissionWeather(metar, min_wind=min_wind, max_wind=max_wind)

    if time:
        try:
            time = MissionTime.from_string(time)
        except ValueError:
            return f'badly formatted time string: {time}'

    if not metar and not time:
        return 'nothing to do!'

    with Miz(infile) as miz:
        if mission_weather:
            LOGGER.debug('applying MissionWeather')
            if not mission_weather.apply_to_miz(miz):
                return 'error while applying METAR to mission'
        if time:
            LOGGER.debug('applying MissionTime')
            if not time.apply_to_miz(miz):
                return 'error while setting time on mission'

        try:
            miz.zip(outfile)
            return ''
        except OSError:
            return f'permission error: cannot edit "{outfile}"; maybe it is in use ?'
