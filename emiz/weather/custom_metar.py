# coding=utf-8

from metar.Datatypes import UnitsError, pressure
from metar.Metar import Metar


class CustomPressure(pressure):
    legal_units = ["MB", "HPA", "IN", "MM"]

    def value(self, units=None):
        """Return the pressure in the specified units."""
        if units == None:
            return self._value
        else:
            if not units.upper() in CustomPressure.legal_units:
                raise UnitsError("unrecognized pressure unit: '" + units + "'")
            units = units.upper()
        if units == self._units:
            return self._value
        if self._units == "IN":
            mb_value = self._value * 33.86398
        elif self._units == "MM":
            mb_value = self._value * 1.3332239
        else:
            mb_value = self._value
        if units == "MB" or units == "HPA":
            return mb_value
        elif units == "IN":
            return mb_value / 33.86398
        elif units == "MM":
            return mb_value / 1.3332239
        else:
            raise UnitsError("unrecognized pressure unit: '" + units + "'")


    def string(self, units=None):
        """Return a string representation of the pressure, using the given units."""
        if not units:
            units = self._units
        else:
            if not units.upper() in CustomPressure.legal_units:
                raise UnitsError("unrecognized pressure unit: '" + units + "'")
            units = units.upper()
        val = self.value(units)
        if units == "MB":
            return "%.0f mb" % val
        elif units == "HPA":
            return "%.0f hPa" % val
        elif units == "IN":
            return "%.2f inches" % val
        elif units == "MM":
            return "%.0f mmHg" % val


class CustomMetar(Metar):

    def __init__(self, metarcode, month=None, year=None, utcdelta=None):
        Metar.__init__(self, metarcode, month, year, utcdelta)
        self.press = CustomPressure(self.press.value('mb'))

    def string(self):
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
            lines.append(f"pressure: "
                         f"{self.press.string('MB')} - "
                         f"{self.press.string('IN')} - "
                         f"{self.press.string('MM')}"
                         )
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


if __name__ == '__main__':
    metar = CustomMetar('UGTB 041500Z 14007KT 9999 FEW020 BKN038CB OVC052 11/08 Q1030 R13R/CLRD70 NOSIG')
    print(metar.string())
