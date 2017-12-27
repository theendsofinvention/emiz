# coding=utf-8
"""
Subclass Metar.pressure to add MM unit (millimeter or mercury)
"""

from metar.Datatypes import UnitsError, pressure


class CustomPressure(pressure):
    """
    Subclass Metar.pressure to add MM unit (millimeter or mercury)
    """
    legal_units = ["MB", "HPA", "IN", "MM"]

    def value(self, units=None):
        """Return the pressure in the specified units."""
        if units is None:
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

    def string(self, units=None) -> str:
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

        raise ValueError(units)
