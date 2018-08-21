# coding=utf-8
"""
Simple parser for AWV results
"""

import typing

import elib

from emiz.weather.awc.exc import NoMetarForStation

LOGGER = elib.custom_logging.get_logger('EMIZ')


# pylint: disable=too-many-instance-attributes
class AWCResult:
    """
    Parse CSV data coming from AWC into a usable object
    """

    def __init__(self, icao: str, raw_csv_data: typing.List[str]) -> None:
        errors, warnings, time, source, count, headings, *metars = raw_csv_data
        if errors != 'No errors':
            LOGGER.error(errors)
        if warnings != 'No warnings':
            LOGGER.warning(warnings)
        self._errors = errors
        self._warnings = warnings
        self._time = time
        self._source = source
        self._count = count
        if self._count == '0 results':
            raise NoMetarForStation(icao)
        self._headings = headings
        self._metars = metars
        self.__parsed_metar: typing.Optional[dict] = None
        print(self._headings)

    @property
    def _parsed_metar(self) -> dict:
        if self.__parsed_metar is None:
            self.__parsed_metar = dict(zip(self._headings.split(','), self._metars[0].split(',')))
        return self.__parsed_metar

    @property
    def station_id(self) -> str:
        """
        Returns: ICAO code for this METAR
        """
        return self._parsed_metar['station_id']

    # @property
    # def observation_time(self):
    #     return self._parsed_metar['observation_time']
    #
    # @property
    # def latitude(self):
    #     return self._parsed_metar['latitude']
    #
    # @property
    # def longitude(self):
    #     return self._parsed_metar['longitude']

    # @property
    # def temp_c(self):
    #     return self._parsed_metar['temp_c']
    #
    # @property
    # def dewpoint_c(self):
    #     return self._parsed_metar['dewpoint_c']
    #
    # @property
    # def wind_dir_degrees(self):
    #     return self._parsed_metar['wind_dir_degrees']
    #
    # @property
    # def wind_speed_kt(self):
    #     return self._parsed_metar['wind_speed_kt']

    # @property
    # def wind_gust_kt(self):
    #     return self._parsed_metar['wind_gust_kt']
    #
    # @property
    # def visibility_statute_mi(self):
    #     return self._parsed_metar['visibility_statute_mi']
    #
    # @property
    # def altim_in_hg(self):
    #     return self._parsed_metar['altim_in_hg']
    #
    # @property
    # def sea_level_pressure_mb(self):
    #     return self._parsed_metar['sea_level_pressure_mb']

    # @property
    # def corrected(self):
    #     return self._parsed_metar['corrected']
    #
    # @property
    # def auto(self):
    #     return self._parsed_metar['auto']
    #
    # @property
    # def auto_station(self):
    #     return self._parsed_metar['auto_station']
    #
    # @property
    # def maintenance_indicator_on(self):
    #     return self._parsed_metar['maintenance_indicator_on']

    # @property
    # def no_signal(self):
    #     return self._parsed_metar['no_signal']
    #
    # @property
    # def lightning_sensor_off(self):
    #     return self._parsed_metar['lightning_sensor_off']
    #
    # @property
    # def freezing_rain_sensor_off(self):
    #     return self._parsed_metar['freezing_rain_sensor_off']
    #
    # @property
    # def present_weather_sensor_off(self):
    #     return self._parsed_metar['present_weather_sensor_off']

    # @property
    # def wx_string(self):
    #     return self._parsed_metar['wx_string']
    #
    # @property
    # def sky_cover(self):
    #     return self._parsed_metar['sky_cover']
    #
    # @property
    # def cloud_base_ft_agl(self):
    #     return self._parsed_metar['cloud_base_ft_agl']

    @property
    def flight_category(self) -> str:
        """
        Returns: flight category in effect (VFR, IFR, ...)
        """
        return self._parsed_metar['flight_category']

    # @property
    # def three_hr_pressure_tendency_mb(self):
    #     return self._parsed_metar['three_hr_pressure_tendency_mb']
    #
    # @property
    # def maxT_c(self):
    #     return self._parsed_metar['maxT_c']
    #
    # @property
    # def minT_c(self):
    #     return self._parsed_metar['minT_c']

    # @property
    # def maxT24hr_c(self):
    #     return self._parsed_metar['maxT24hr_c']
    #
    # @property
    # def minT24hr_c(self):
    #     return self._parsed_metar['minT24hr_c']
    #
    # @property
    # def precip_in(self):
    #     return self._parsed_metar['precip_in']
    #
    # @property
    # def pcp3hr_in(self):
    #     return self._parsed_metar['pcp3hr_in']
    #
    # @property
    # def pcp6hr_in(self):
    #     return self._parsed_metar['pcp6hr_in']

    # @property
    # def pcp24hr_in(self):
    #     return self._parsed_metar['pcp24hr_in']
    #
    # @property
    # def snow_in(self):
    #     return self._parsed_metar['snow_in']
    #
    #
    # @property
    # def vert_vis_ft(self):
    #     return self._parsed_metar['vert_vis_ft']
    #
    #
    # @property
    # def metar_type(self):
    #     return self._parsed_metar['metar_type']

    # @property
    # def elevation_m(self):
    #     return self._parsed_metar['elevation_m']

    @property
    def raw_metar(self):
        """
        Returns: raw METAR string
        """
        return self._parsed_metar['raw_text']
