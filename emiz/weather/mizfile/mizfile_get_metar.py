# coding=utf-8
"""
Builds a dummy METAR string from a mission file
"""

import re
import typing
from datetime import datetime

import elib

import emiz.weather.utils
from emiz.mission import Mission, Weather
from emiz.miz import Miz

LOGGER = elib.custom_logging.get_logger('EMIZ')


class _MetarFromMission:
    precipitation_table = {
        0: '',
        1: 'RA',
        2: 'SN',
        3: '+RA',
        4: '+SN',
    }

    _clouds_density_table = density = {
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

    def __init__(
            self,
            mission_file: str,
            icao: typing.Optional[str] = 'XXXX',
            time: typing.Optional[str] = None,
    ) -> None:
        self._icao = icao
        self._time = self._set_time(time)
        with Miz(mission_file) as miz:
            self._mission: Mission = miz.mission

    @staticmethod
    def _set_time(time: typing.Optional[str]) -> str:
        if time is None:
            now = datetime.utcnow()
            day = now.day
            hour = now.hour
            minute = now.minute
            return f'{day:02}{hour:02}{minute:02}Z'
        return time

    @property
    def _weather(self) -> Weather:
        return self._mission.weather  # type: ignore

    @property
    def _wind(self) -> str:
        wind_dir = emiz.weather.utils.reverse_direction(self._weather.wind_at_ground_level_dir)
        wind_speed = int(self._weather.wind_at_ground_level_speed)
        return f'{wind_dir:03}{wind_speed:02}MPS'

    @property
    def _precipitations(self) -> str:
        return self.precipitation_table[self._weather.precipitations]

    @property
    def _clouds(self) -> str:

        if self._weather.cloud_density == 0:
            return ''

        density = self._clouds_density_table[self._weather.cloud_density]
        base = int(round(self._weather.cloud_base * 3.28084, -2) / 100)
        return f'{density}{base:03}'

    @property
    def _temperature(self) -> str:
        temperature = self._weather.temperature
        minus = 'M' if temperature < 0 else ''
        temperature = abs(temperature)
        return f'{minus}{temperature:02}/{minus}{temperature:02}'

    @property
    def _pressure(self) -> str:
        hpa = round(self._weather.qnh / 0.75006156130264)
        return f'Q{hpa}'

    @property
    def _qualifier(self) -> str:
        return 'NOSIG'

    @property
    def _visibility(self) -> str:
        _visibility = int(min(self._weather.visibility, 9999))
        if self._weather.fog_enabled:
            _visibility = int(min(self._weather.fog_visibility, _visibility))

        if _visibility == 9999 and int(round(self._weather.cloud_base * 3.28084, -2)) >= 5000:
            return 'CAVOK'

        return '{:04d}M'.format(_visibility)

    @property
    def metar(self) -> str:
        """
        Builds a METAR string from a MIZ file

        A lots of information is inferred from what information we have available in DCS. There constraints in the way
        MIZ files are built, with precipitations for example.

        Returns: METAR string
        """
        metar = f'{self._icao} ' \
                f'{self._time} ' \
                f'{self._wind} ' \
                f'{self._visibility} ' \
                f'{self._precipitations} ' \
                f'{self._clouds} ' \
                f'{self._temperature} ' \
                f'{self._pressure} ' \
                f'{self._qualifier}'
        return re.sub(' +', ' ', metar)

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
    return _MetarFromMission(
        mission_file=mission_file,
        icao=icao,
        time=time,
    ).metar
