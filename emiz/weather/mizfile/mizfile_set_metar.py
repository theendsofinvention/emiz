# coding=utf-8
"""
Applies a METAR to a MIZ file
"""
import typing
from pathlib import Path

import elib.path
from metar import Metar

from emiz import MAIN_LOGGER
from emiz.miz import Miz

from .. import custom_metar, mission_weather

LOGGER = MAIN_LOGGER.getChild(__name__)


def set_weather_from_metar(
        metar: typing.Union[Metar.Metar, str],
        in_file: typing.Union[str, Path],
        out_file: typing.Union[str, Path] = None
) -> typing.Tuple[typing.Union[str, None], typing.Union[str, None]]:
    """
    Applies the weather from a METAR object to a MIZ file

    Args:
        metar: metar object
        in_file: path to MIZ file
        out_file: path to output MIZ file (will default to in_file)

    Returns: tuple of error, success

    """
    error, metar = custom_metar.CustomMetar.get_metar(metar)

    if error:
        return error, None

    LOGGER.debug(f'METAR: {metar.code}')

    in_file = elib.path.ensure_file(in_file)

    if out_file is None:
        out_file = in_file
    else:
        out_file = elib.path.ensure_file(out_file, must_exist=False)
    LOGGER.debug(f'applying metar: {in_file} -> {out_file}')

    try:
        LOGGER.debug('building MissionWeather')
        _mission_weather = mission_weather.MissionWeather(metar)

        with Miz(str(in_file)) as miz:
            _mission_weather.apply_to_miz(miz)
            miz.zip(str(out_file))
            return None, f'successfully applied METAR to {in_file}'

    except ValueError:
        error = f'Unable to apply METAR string to the mission.\n' \
                f'This is most likely due to a freak value, this feature is still experimental.\n' \
                f'I will fix it ASAP !'
        return error, None
