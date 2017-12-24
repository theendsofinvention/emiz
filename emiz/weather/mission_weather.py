# coding=utf-8
"""
Manage mission weather
"""

from emiz import MAIN_LOGGER
import random
import re
import typing
from datetime import date, datetime

from metar.Metar import Metar

from emiz.miz import Mission, Miz

LOGGER = MAIN_LOGGER.getChild(__name__)

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

Y = 2000

SEASONS = [
    ('winter', 5, (date(Y, 1, 1), date(Y, 3, 20))),
    ('spring', 10, (date(Y, 3, 21), date(Y, 6, 20))),
    ('summer', 20, (date(Y, 6, 21), date(Y, 9, 22))),
    ('autumn', 10, (date(Y, 9, 23), date(Y, 12, 20))),
    ('winter', 5, (date(Y, 12, 21), date(Y, 12, 31))),
]


def _get_season() -> typing.Tuple[str, int]:
    """
    Finds the current season based on now() and gives a dummy temperature

    Returns: tuple of season name, temperature

    """
    now = datetime.now().date().replace(year=Y)
    return next((season, temp) for season, temp, (start, end) in SEASONS if start <= now <= end)


def _hpa_to_mmhg(pressure) -> int:
    """
    Converts pressure in hpa to mmhg
    Args:
        pressure: pressure to convert

    Returns: pressure in mmhg

    """
    return int(pressure * 0.75006156130264)


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
        self.precip = 0
        self.cloud_density = 0
        self.cloud_base = 300
        self.cloud_thickness = 200
        self.force_cloud_density = 0
        self.force_temperature = 999
        self._parse_precip()
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
            LOGGER.info('QNH is missing, returning standard QNH')
            return 760
        return _hpa_to_mmhg(self.metar.press.value())

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

    def _parse_precip(self):
        """

        Sets precipitation and optional minimal cloud density

        """
        if 'rain' in self.metar.present_weather():
            self.precip = 1
            self.force_cloud_density = 5
        if 'snow' in self.metar.present_weather():
            self.precip = 3
            self.force_cloud_density = 5
            self.force_temperature = 0
        if 'storm' in self.metar.present_weather():
            if self.precip == 2:
                self.precip = 4
            else:
                self.precip = 3
            self.force_cloud_density = 9

    def _parse_clouds(self):
        """

        Sets cloud density

        """
        layers = {}
        for skyi in self.metar.sky:
            cover, height, _ = skyi
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
        return int(self.metar.temp.value('C'))

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

        miz.mission.weather.wind_at_ground_level_dir = self.wind_at_ground_level_dir
        miz.mission.weather.wind_at_ground_level_speed = self.wind_at_ground_level_speed
        miz.mission.weather.wind_at2000_dir = self._deviate_direction(self.wind_dir, 40)
        miz.mission.weather.wind_at2000_speed = self._deviate_wind_speed(5 + self.wind_speed * 2)
        miz.mission.weather.wind_at8000_dir = self._deviate_direction(self.wind_dir, 80)
        miz.mission.weather.wind_at8000_speed = self._deviate_wind_speed(10 + self.wind_speed * 3)
        miz.mission.weather.turbulence_at_ground_level = self.turbulence

        miz.mission.weather.atmosphere_type = 0
        miz.mission.weather.qnh = self.qnh

        miz.mission.weather.visibility = self.visibility
        miz.mission.weather.fog_thickness = 1000
        if self.fog_vis:
            miz.mission.weather.fog_visibility = self.fog_vis
            miz.mission.weather.fog_enabled = True

        miz.mission.weather.cloud_density = max(self.force_cloud_density, self.cloud_density)
        miz.mission.weather.cloud_thickness = self.cloud_thickness
        miz.mission.weather.cloud_base = self.cloud_base
        miz.mission.weather.precipitations = self.precip

        miz.mission.weather.temperature = self.temperature

        return True


# pylint: disable=too-many-locals
def build_metar_from_mission(
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

    def _get_wind(mission):
        wind_dir = MissionWeather.reverse_direction(mission.weather.wind_at_ground_level_dir)
        wind_speed = int(mission.weather.wind_at_ground_level_speed)
        return f'{wind_dir:03}{wind_speed:02}MPS'

    def _get_precip(mission: Mission):
        precip = {
            0: '',
            1: 'RA',
            2: 'SN',
            3: '+RA',
            4: '+SN',
        }
        return precip[mission.weather.precipitations]

    def _get_clouds(mission: Mission):
        density = {
            0: 'CLR',
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
        density = density[mission.weather.cloud_density]
        base = int(round(mission.weather.cloud_base * 3.28084, -2))
        return f'{density}{base:04}'

    def _get_temp(mission: Mission):
        temp = mission.weather.temperature
        minus = 'M' if temp < 0 else ''
        temp = abs(temp)
        return f'{minus}{temp:02}/{minus}{temp:02}'

    def _get_pressure(mission: Mission):
        pres = mission.weather.qnh
        hpa = round(pres / 0.75006156130264)
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
    precip = _get_precip(mission)
    clouds = _get_clouds(mission)
    temp = _get_temp(mission)
    pres = _get_pressure(mission)
    qual = 'NOSIG'

    if visibility == 9999 and int(round(mission.weather.cloud_base * 3.28084, -2)) >= 5000:
        visibility = 'CAVOK'

    metar = f'{icao} {time} {wind} {visibility} {precip} {clouds} {temp} {pres} {qual}'
    return re.sub(' +', ' ', metar)
