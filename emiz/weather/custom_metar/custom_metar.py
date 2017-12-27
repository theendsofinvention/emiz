# coding=utf-8
"""
Subclass metar.Metar.Metar (sic) to add functionality
"""
import typing

from metar.Metar import Metar, ParserError

from .. import noaa
from ... import MAIN_LOGGER
from .custom_metar_pressure import CustomPressure

LOGGER = MAIN_LOGGER.getChild(__name__)


class CustomMetar(Metar):
    """
    Subclass metar.Metar.Metar (sic) to add functionality
    """

    def __init__(self, metar_code, month=None, year=None, utc_delta=None):
        LOGGER.debug(f'creating METAR from: {metar_code}')
        Metar.__init__(self, metar_code, month, year, utc_delta)
        self.press = CustomPressure(self.press.value('mb'))

    @staticmethod
    def get_metar(
            metar: typing.Union[str, 'CustomMetar']
    ) -> typing.Tuple[typing.Union[str, None], typing.Union['CustomMetar', None]]:
        """
        Builds a CustomMetar object from a CustomMetar object (returns it), an ICAO code or a METAR string

        Args:
            metar: CustomMetar object, ICAO string or METAR string

        Returns: CustomMetar object

        """
        error = None
        if isinstance(metar, CustomMetar):
            return None, metar
        elif isinstance(metar, str):
            LOGGER.debug(f'building CustomMetar from: {metar}')
            if len(metar) == 4:
                LOGGER.debug('retrieving METAR from ICAO')
                error, metar = noaa.retrieve_metar(metar)
        else:
            error = f'expected a string or or a CustomMetar object, got: {type(metar)}'

        if error:
            return error, None

        try:
            return None, CustomMetar(metar_code=metar)
        except ParserError:
            return f'Unable to parse METAR: {metar}', None

    # pylint: disable=too-many-branches
    def string(self):  # noqa: C901
        """
        Return a human-readable version of the decoded report.
        """
        lines = ["station: %s" % self.station_id]
        if self.type:
            lines.append("type: %s" % self.report_type())
        if self.time:
            lines.append("time: %s" % self.time.ctime())
        if self.temp:
            lines.append("temperature: %s" % self.temp.string("C"))
        if self.dewpt:
            lines.append("dew point: %s" % self.dewpt.string("C"))
        if self.wind_speed:
            lines.append("wind: %s" % self.wind())
        if self.wind_speed_peak:
            lines.append("peak wind: %s" % self.peak_wind())
        if self.wind_shift_time:
            lines.append("wind shift: %s" % self.wind_shift())
        if self.vis:
            lines.append("visibility: %s" % self.visibility())
        if self.runway:
            lines.append("visual range: %s" % self.runway_visual_range())
        if self.press:
            lines.append(f"pressure: {self.press.string('MB')} {self.press.string('IN')} {self.press.string('MM')}")
        if self.weather:
            lines.append("weather: %s" % self.present_weather())
        if self.sky:
            lines.append("sky: %s" % self.sky_conditions("\n     "))
        if self.press_sea_level:
            lines.append("sea-level pressure: %s" % self.press_sea_level.string("mb"))
        if self.max_temp_6hr:
            lines.append("6-hour max temp: %s" % str(self.max_temp_6hr))
        if self.max_temp_6hr:
            lines.append("6-hour min temp: %s" % str(self.min_temp_6hr))
        if self.max_temp_24hr:
            lines.append("24-hour max temp: %s" % str(self.max_temp_24hr))
        if self.max_temp_24hr:
            lines.append("24-hour min temp: %s" % str(self.min_temp_24hr))
        if self.precip_1hr:
            lines.append("1-hour precipitation: %s" % str(self.precip_1hr))
        if self.precip_3hr:
            lines.append("3-hour precipitation: %s" % str(self.precip_3hr))
        if self.precip_6hr:
            lines.append("6-hour precipitation: %s" % str(self.precip_6hr))
        if self.precip_24hr:
            lines.append("24-hour precipitation: %s" % str(self.precip_24hr))
        if self._remarks:
            lines.append("remarks:")
            lines.append("- " + self.remarks("\n- "))
        if self._unparsed_remarks:
            lines.append("- " + ' '.join(self._unparsed_remarks))
        lines.append("METAR: " + self.code)
        return "\n".join(lines)

    def _handlePressure(self, d):
        """
        Parse an altimeter-pressure group.

        The following attributes are set:
            press    [int]
        """
        press = d['press']
        if press != '////':
            press = float(press.replace('O', '0'))
            if d['unit']:
                if d['unit'] == 'A' or (d['unit2'] and d['unit2'] == 'INS'):
                    self.press = CustomPressure(press / 100, 'IN')
                elif d['unit'] == 'SLP':
                    if press < 500:
                        press = press / 10 + 1000
                    else:
                        press = press / 10 + 900
                    self.press = CustomPressure(press, 'MB')
                    self._remarks.append("sea-level pressure %.1fhPa" % press)
                else:
                    self.press = CustomPressure(press, 'MB')
            elif press > 2500:
                self.press = CustomPressure(press / 100, 'IN')
            else:
                self.press = CustomPressure(press, 'MB')

    # noinspection SpellCheckingInspection
    def _handleSealvlPressRemark(self, d):
        """
        Parse the sea-level pressure remark group.
        """
        value = float(d['press']) / 10.0
        if value < 50:
            value += 1000
        else:
            value += 900
        if not self.press:
            self.press = CustomPressure(value, "MB")
        self.press_sea_level = CustomPressure(value, "MB")
