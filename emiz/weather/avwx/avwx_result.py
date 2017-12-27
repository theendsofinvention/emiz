# coding=utf-8
"""
Represents the result of a query to AVWX API
"""
from collections import defaultdict

from emiz import MAIN_LOGGER

LOGGER = MAIN_LOGGER.getChild(__name__)


# pylint: disable=too-few-public-methods
class _AVWXProp:
    """
    Represents a property of AVWX result (simple descriptor)
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, _):
        if obj is None:
            return self
        return obj.data[self.func.__name__]


# noinspection SpellCheckingInspection
# pylint: disable=too-many-public-methods
class AVWXResult:
    """
    Represents the result of a query to AVWX API
    """
    default_value = 'NOTSET'

    @staticmethod
    def default_factory():
        """Returns default value for unset property in the data dict"""
        return AVWXResult.default_value

    def __init__(self, **kwargs):
        self.data = defaultdict(default_factory=self.default_factory)
        self.data.update(kwargs)

    @_AVWXProp
    def altimeter(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def cloudlist(self) -> list:
        """AVWX result property"""
        pass

    @_AVWXProp
    def dewpoint(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def flightrules(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def info(self) -> dict:
        """AVWX result property"""
        pass

    @_AVWXProp
    def meta(self) -> dict:
        """AVWX result property"""
        pass

    @_AVWXProp
    def otherlist(self) -> list:
        """AVWX result property"""
        pass

    @_AVWXProp
    def rawreport(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def remarks(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def remarksinfo(self) -> dict:
        """AVWX result property"""
        pass

    @_AVWXProp
    def runwayvislist(self) -> list:
        """AVWX result property"""
        pass

    @_AVWXProp
    def speech(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def station(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def summary(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def temperature(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def time(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def translations(self) -> dict:
        """AVWX result property"""
        pass

    @_AVWXProp
    def units(self) -> dict:
        """AVWX result property"""
        pass

    @_AVWXProp
    def visibility(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def winddirection(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def windgust(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def windspeed(self) -> str:
        """AVWX result property"""
        pass

    @_AVWXProp
    def windvariabledir(self) -> list:
        """AVWX result property"""
        pass
