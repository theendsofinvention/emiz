# coding=utf-8
"""
Builds a dummy METAR string from a mission file
"""

import re
from datetime import datetime

import emiz.weather.utils
from emiz import MAIN_LOGGER
from emiz.miz import Mission, Miz

LOGGER = MAIN_LOGGER.getChild(__name__)


# pylint: disable=too-many-locals
def get_metar_from_mission(
        mission_file: str,
        icao: str = 'XXXX',
        time: str = None,
) -> str:
    """
    Builds a dummy METAR string from a mission file

    Args:
        mission_file: input mission file
        icao: dummy ICAO (defaults to XXXX)
        time: dummy time (defaults to now())

    Returns: METAR str

    """

    def _get_wind(mission_: Mission):
        wind_dir = emiz.weather.utils.reverse_direction(mission_.weather.wind_at_ground_level_dir)
        wind_speed = int(mission_.weather.wind_at_ground_level_speed)
        return f'{wind_dir:03}{wind_speed:02}MPS'

    def _get_precipitations(mission_: Mission):
        precipitations_ = {
            0: '',
            1: 'RA',
            2: 'SN',
            3: '+RA',
            4: '+SN',
        }
        return precipitations_[mission_.weather.precipitations]

    def _get_clouds(mission_: Mission):
        density = {
            0: '',
            1: 'FEW',
            2: 'FEW',
            3: 'FEW',
            4: 'SCT',
            5: 'SCT',
            6: 'SCT',
            7: 'BKN',
            8: 'BKN',
            9: 'OVC',
            10: 'OVC',
        }
        if mission_.weather.cloud_density == 0:
            return ''

        density = density[mission_.weather.cloud_density]
        base = int(round(mission_.weather.cloud_base * 3.28084, -2) / 100)
        return f'{density}{base:03}'

    def _get_temp(mission_: Mission):
        temperature = mission_.weather.temperature
        minus = 'M' if temperature < 0 else ''
        temperature = abs(temperature)
        return f'{minus}{temperature:02}/{minus}{temperature:02}'

    def _get_pressure(mission_: Mission):
        hpa = round(mission_.weather.qnh / 0.75006156130264)
        return f'Q{hpa}'

    if time is None:
        now = datetime.utcnow()
        day = now.day
        hour = now.hour
        minute = now.minute
        time = f'{day:02}{hour:02}{minute:02}Z'
    with Miz(mission_file) as miz:
        mission = miz.mission
    wind = _get_wind(mission)
    visibility = min(mission.weather.visibility, 9999)
    if mission.weather.fog_enabled:
        visibility = min(mission.weather.fog_visibility, visibility)
    precipitations = _get_precipitations(mission)
    clouds = _get_clouds(mission)
    temp = _get_temp(mission)
    pres = _get_pressure(mission)
    # noinspection SpellCheckingInspection
    qual = 'NOSIG'

    if visibility == 9999 and int(round(mission.weather.cloud_base * 3.28084, -2)) >= 5000:
        # noinspection SpellCheckingInspection
        visibility = 'CAVOK'
    else:
        visibility = ('{:04d}M'.format(visibility))

    metar = f'{icao} {time} {wind} {visibility} {precipitations} {clouds} {temp} {pres} {qual}'
    return re.sub(' +', ' ', metar)
