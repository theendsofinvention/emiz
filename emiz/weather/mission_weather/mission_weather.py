# coding=utf-8
"""
Manage mission weather
"""

import random
import typing
from datetime import date, datetime

from metar.Metar import Metar

from emiz import MAIN_LOGGER

from ..utils import hpa_to_mmhg

LOGGER = MAIN_LOGGER.getChild(__name__)

Y = 2000

SEASONS = [
    ('winter', 5, (date(Y, 1, 1), date(Y, 3, 20))),
    ('spring', 10, (date(Y, 3, 21), date(Y, 6, 20))),
    ('summer', 20, (date(Y, 6, 21), date(Y, 9, 22))),
    ('autumn', 10, (date(Y, 9, 23), date(Y, 12, 20))),
    ('winter', 5, (date(Y, 12, 21), date(Y, 12, 31))),
]

SKY_COVER = {
    "SKC": (0, 0),
    "CLR": (0, 0),
    "NSC": (0, 0),
    "NCD": (0, 0),
    "FEW": (1, 3),
    "SCT": (4, 6),
    "BKN": (7, 8),
    "OVC": (9, 10),
    "///": (0, 0),
    "VV": (0, 0)
}


def _get_season() -> typing.Tuple[str, int]:
    """
    Finds the current season based on now() and gives a dummy temperature

    Returns: tuple of season name, temperature

    """
    now = datetime.now().date().replace(year=Y)
    return next((season, temp) for season, temp, (start, end) in SEASONS if start <= now <= end)


class MissionWeather:  # pylint: disable=too-many-instance-attributes
    """
    Struct for Mission weather
    """

    def __init__(
            self,
            metar: Metar,
            min_wind: int = 0,
            max_wind: int = 40,
    ):
        self.metar = metar
        self.wind_dir = None
        self.wind_speed = None
        self._min_wind = min_wind
        self._max_wind = max_wind
        self.fog_vis = None
        self.precipitations = 0
        self.cloud_density = 0
        self.cloud_base = 300
        self.cloud_thickness = 200
        self.force_cloud_density = 0
        self.force_temperature = 999
        self._parse_precipitations()
        self._parse_clouds()

    @staticmethod
    def _random_direction() -> int:
        return random.randint(0, 359)

    @staticmethod
    def reverse_direction(heading: int) -> int:
        """
        Inverts a direction in degrees

        Args:
            heading: original direction

        Returns: direction plus or minus 180°

        """
        if heading >= 180:
            return int(heading - 180)

        return int(heading + 180)

    @staticmethod
    def _normalize_direction(heading: int) -> int:
        """
        Make sure that 0 < heading < 360

        Args:
            heading: base heading

        Returns: corrected heading

        """
        while heading > 359:
            heading = int(heading - 359)
        while heading < 0:
            heading = int(heading + 359)
        return heading

    @staticmethod
    def _gauss(mean: int, sigma: int) -> int:
        """
        Creates a variation from a base value

        Args:
            mean: base value
            sigma: gaussian sigma

        Returns: random value

        """
        return int(random.gauss(mean, sigma))

    @staticmethod
    def _deviate_wind_speed(base_speed: int, sigma: int = None) -> int:
        """
        Creates a variation in wind speed

        Args:
            base_speed: base wind speed
            sigma: sigma value for gaussian variation

        Returns: random wind speed

        """
        if sigma is None:
            sigma = base_speed / 4
        val = MissionWeather._gauss(base_speed, sigma)
        if val < 0:
            return 0
        return min(val, 50)

    @staticmethod
    def _deviate_direction(base_heading, sigma) -> int:
        """
        Creates a variation in direction

        Args:
            base_heading: base direction
            sigma: sigma value for gaussian variation

        Returns: random direction

        """
        val = MissionWeather._gauss(base_heading, sigma)
        val = MissionWeather._normalize_direction(val)
        return val

    @property
    def wind_at_ground_level_dir(self) -> int:
        """

        Returns: direction of wind at ground level

        """
        if self.metar.wind_dir is None:
            LOGGER.info('wind is variable, making a random value')
            val = self._random_direction()
        else:
            val = self.reverse_direction(self.metar.wind_dir.value())
        self.wind_dir = val
        return val

    @property
    def wind_at_ground_level_speed(self) -> int:
        """

        Returns: speed of wind at ground level

        """
        if self.metar.wind_speed is None:
            LOGGER.info('wind speed is missing, making a random value')
            val = random.randint(self._min_wind, self._max_wind)
        else:
            val = int(self.metar.wind_speed.value('MPS'))
        self.wind_speed = val
        return val

    @property
    def qnh(self) -> int:
        """

        Returns: atmospheric pressure

        """
        if self.metar.press is None:
            LOGGER.info('QNH is missing, returning standard QNH: 760')
            return 760
        return hpa_to_mmhg(self.metar.press.value())

    @property
    def visibility(self) -> int:
        """

        Returns: visibility in kilometers

        """
        if self.metar.vis is None:
            LOGGER.debug('visibility is missing, returning maximum')
            return 800000
        val = int(self.metar.vis.value())
        if val < 10000:
            self.fog_vis = min(6000, val)
        return val

    def _parse_precipitations(self):
        """

        Sets precipitation and optional minimal cloud density

        """
        if 'rain' in self.metar.present_weather():
            self.precipitations = 1
            self.force_cloud_density = 5
        if 'snow' in self.metar.present_weather():
            self.precipitations = 3
            self.force_cloud_density = 5
            self.force_temperature = 0
        if 'storm' in self.metar.present_weather():
            if self.precipitations == 2:
                self.precipitations = 4
            else:
                self.precipitations = 3
            self.force_cloud_density = 9

    def _parse_clouds(self):
        """

        Sets cloud density

        """
        layers = {}
        for sky_info in self.metar.sky:
            cover, height, _ = sky_info
            if height:
                height = int(height.value('M'))
                height = max(height, 300)
                height = min(height, 5000)
                cover = random.randint(*SKY_COVER[cover])
                layers[cover] = height
        if layers:
            max_cover = max([key for key in layers])
            self.cloud_density = max_cover
            self.cloud_base = layers[max_cover]
            self.cloud_thickness = int(max_cover / 10 * 2000)

    @property
    def temperature(self):
        """

        Sets temperature

        """
        if self.metar.temp is None:
            season, temp = _get_season()
            LOGGER.debug(f'no temperature given, since it is {season}, defaulting to {temp}')
            return temp
        value = min(self.force_temperature, int(self.metar.temp.value('C')))
        return value

    @property
    def turbulence(self) -> int:
        """

        Sets turbulence from base wind value

        """
        if self.metar.wind_gust is None:
            return 0
        val = int(self.metar.wind_gust.value('MPS'))
        if self.wind_speed >= val:
            return 0
        return int(min((val - self.wind_speed) * 10, 60))

    def apply_to_miz(self, miz):
        """
        Applies weather to an opened Miz file (the mission will be mutated)

        Args:
            miz: source miz

        Returns: True

        """

        report = ['Building mission with weather:']

        miz.mission.weather.wind_at_ground_level_dir = self.wind_at_ground_level_dir
        miz.mission.weather.wind_at_ground_level_speed = self.wind_at_ground_level_speed
        miz.mission.weather.wind_at2000_dir = self._deviate_direction(self.wind_dir, 40)
        miz.mission.weather.wind_at2000_speed = self._deviate_wind_speed(5 + self.wind_speed * 2)
        miz.mission.weather.wind_at8000_dir = self._deviate_direction(self.wind_dir, 80)
        miz.mission.weather.wind_at8000_speed = self._deviate_wind_speed(10 + self.wind_speed * 3)
        miz.mission.weather.turbulence_at_ground_level = self.turbulence

        _ground = f'{miz.mission.weather.wind_at_ground_level_dir}/{miz.mission.weather.wind_at_ground_level_speed}'
        _at2000 = f'{miz.mission.weather.wind_at2000_dir}/{miz.mission.weather.wind_at2000_speed}'
        _at8000 = f'{miz.mission.weather.wind_at8000_dir}/{miz.mission.weather.wind_at8000_speed}'
        _turbulence = f'{miz.mission.weather.turbulence_at_ground_level}'

        wind = f'Wind:' \
               f'\n\tGround: {_ground}' \
               f'\n\t2000m: {_at2000}' \
               f'\n\t8000m: {_at8000}' \
               f'\n\tTurbulence: {_turbulence}'

        report.append(wind)

        miz.mission.weather.atmosphere_type = 0
        miz.mission.weather.qnh = self.qnh

        report.append(f'Atmosphere type: {miz.mission.weather.atmosphere_type}')
        report.append(f'QNH: {miz.mission.weather.qnh}')

        miz.mission.weather.visibility = self.visibility
        if self.fog_vis:
            miz.mission.weather.fog_thickness = 1000
            miz.mission.weather.fog_visibility = self.fog_vis
            miz.mission.weather.fog_enabled = True
        else:
            miz.mission.weather.fog_enabled = False
            miz.mission.weather.fog_visibility = 0
            miz.mission.weather.fog_thickness = 0

        visibility = f'Visibility: {miz.mission.weather.visibility}' \
                     f'\n\tFog: {"yes" if miz.mission.weather.fog_enabled else "no"}' \
                     f'\n\tFog thickness: {miz.mission.weather.fog_thickness}' \
                     f'\n\tFog visibility: {miz.mission.weather.fog_visibility}'

        report.append(visibility)

        miz.mission.weather.temperature = self.temperature

        report.append(f'Temperature: {self.temperature}°C')

        miz.mission.weather.cloud_density = max(self.force_cloud_density, self.cloud_density)
        miz.mission.weather.cloud_thickness = self.cloud_thickness
        miz.mission.weather.cloud_base = self.cloud_base
        miz.mission.weather.precipitations = self.precipitations

        clouds = f'Clouds:' \
                 f'\n\tClouds density: {miz.mission.weather.cloud_density}' \
                 f'\n\tClouds thickness: {miz.mission.weather.cloud_thickness}' \
                 f'\n\tClouds base: {miz.mission.weather.cloud_base}' \
                 f'\n\tPrecipitations: {miz.mission.weather.precipitations}'

        report.append(clouds)

        LOGGER.debug(f'applying weather: {report}')

        return True
