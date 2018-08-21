# coding=utf-8
"""
Subclass Metar.pressure to add MM unit (millimeter or mercury)
"""
import typing

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
        if units in ("MB", "HPA"):
            return mb_value
        if units == "IN":
            return mb_value / 33.86398
        if units == "MM":
            return mb_value / 1.3332239

        raise UnitsError("unrecognized pressure unit: '" + units + "'")

    def string(self, units: typing.Optional[str] = None) -> str:
        """Return a string representation of the pressure, using the given units."""
        if not units:
            _units: str = self._units
        else:
            if not units.upper() in CustomPressure.legal_units:
                raise UnitsError("unrecognized pressure unit: '" + units + "'")
            _units = units.upper()
        val = self.value(units)
        if _units == "MB":
            return "%.0f mb" % val
        if _units == "HPA":
            return "%.0f hPa" % val
        if _units == "IN":
            return "%.2f inches" % val
        if _units == "MM":
            return "%.0f mmHg" % val

        raise ValueError(_units)
