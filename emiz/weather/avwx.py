# coding=utf-8
# pylint: disable=unsubscriptable-object
"""
Access to AVWX API

https://avwx.rest/documentation
"""

import json
import string
from collections import defaultdict

import requests
import requests.adapters
from elib.custom_random import random_string

from emiz import MAIN_LOGGER

LOGGER = MAIN_LOGGER.getChild(__name__)


PHONETIC = {'A': 'Alpha', 'B': 'Bravo', 'C': 'Charlie', 'D': 'Delta', 'E': 'Echo', 'F': 'Foxtrot', 'G': 'Golf',
            "H": "Hotel", 'I': 'India', 'J': 'Juliet', 'K': 'Kilo', 'L': 'Lima', 'M': 'Mike', 'N': 'November',
            'O': 'Oscar', 'P': 'Papa', 'Q': 'Quebec', 'R': 'Romeo', 'S': 'Sierra', 'T': 'Tango', 'U': 'Uniform',
            'V': 'Victor', 'W': 'Whiskey', 'X': 'Xray', 'Y': 'Yankee', 'Z': 'Zulu'}


# pylint: disable=too-few-public-methods
class AVWXProp:
    """
    Represents a property of AVWX result (simple descriptor)
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, _):
        if obj is None:
            return self
        return obj.data[self.func.__name__]


# pylint: disable=missing-docstring,too-many-public-methods
# noinspection PyMissingOrEmptyDocstring
class AVWXResult:
    """
    Represents the result of a query to AVWX API
    """
    default_value = 'NOTSET'

    @staticmethod
    def default_factory():
        return AVWXResult.default_value

    def __init__(self, **kwargs):
        self.data = defaultdict(default_factory=self.default_factory)
        self.data.update(kwargs)

    @AVWXProp
    def altimeter(self) -> str:
        pass

    @AVWXProp
    def cloudlist(self) -> list:
        pass

    @AVWXProp
    def dewpoint(self) -> str:
        pass

    @AVWXProp
    def flightrules(self) -> str:
        pass

    @AVWXProp
    def info(self) -> dict:
        pass

    @AVWXProp
    def meta(self) -> dict:
        pass

    @AVWXProp
    def otherlist(self) -> list:
        pass

    @AVWXProp
    def rawreport(self) -> str:
        pass

    @AVWXProp
    def remarks(self) -> str:
        pass

    @AVWXProp
    def remarksinfo(self) -> dict:
        pass

    @AVWXProp
    def runwayvislist(self) -> list:
        pass

    @AVWXProp
    def speech(self) -> str:
        pass

    @AVWXProp
    def station(self) -> str:
        pass

    @AVWXProp
    def summary(self) -> str:
        pass

    @AVWXProp
    def temperature(self) -> str:
        pass

    @AVWXProp
    def time(self) -> str:
        pass

    @AVWXProp
    def translations(self) -> dict:
        pass

    @AVWXProp
    def units(self) -> dict:
        pass

    @AVWXProp
    def visibility(self) -> str:
        pass

    @AVWXProp
    def winddirection(self) -> str:
        pass

    @AVWXProp
    def windgust(self) -> str:
        pass

    @AVWXProp
    def windspeed(self) -> str:
        pass

    @AVWXProp
    def windvariabledir(self) -> list:
        pass


# pylint: disable=too-few-public-methods
class AVWX:
    """
    Access to AVWX API

    https://avwx.rest/documentation
    """
    s = requests.Session()
    s.mount('https://avwx.rest', requests.adapters.HTTPAdapter(max_retries=10))

    @staticmethod
    def _query(url, params: dict = None) -> AVWXResult:
        LOGGER.debug(f'querying: {url}')
        req = AVWX.s.get(url, timeout=2, params=params)
        if not req.ok:
            msg = f'failed to retrieve: {url}'
            LOGGER.error(msg)
            raise ConnectionError(msg)
        LOGGER.debug('parsing data')
        orig_data = json.loads(req.content)
        new_data = {}
        LOGGER.debug('sanitizing data keys')
        for key in orig_data:
            new_key = str(key).replace('-', '')
            new_key = new_key.lower()
            new_data[new_key] = orig_data[key]
        try:
            LOGGER.debug('returning AVWXResult instance')
            return AVWXResult(**new_data)
        except TypeError:
            import pprint
            LOGGER.error(f'invalid data was:\n{pprint.pformat(orig_data)}')
            raise

    @staticmethod
    def query_icao(icao: str) -> AVWXResult:
        """
        Queries AVWX API for weather at given station

        Args:
            icao: ICAO code of the station

        Returns: AVWXResult instance

        """
        params = {
            'options': 'info,speech,summary,translate'
        }
        LOGGER.info(f'getting METAR info for ICAO: {icao}')
        return AVWX._query(f'https://avwx.rest/api/metar/{icao}', params=params)

    @staticmethod
    def metar_to_speech(metar: str) -> str:
        """
        Creates a speakable text from a METAR

        Args:
            metar: METAR string to use

        Returns: speakable METAR for TTS

        """
        LOGGER.info(f'getting speech text from METAR: {metar}')
        params = {
            'report': metar,
            'options': 'info,speech,summary'
        }
        result = AVWX._query(f'https://avwx.rest/api/parse/metar', params=params)
        intro = f'ATIS information for {result.info["City"]} {result.info["Name"]}.'
        identifier = f'Advise you have information {PHONETIC[random_string(1, string.ascii_uppercase)]}.'
        speech = f'{intro} {result.speech}. {identifier}'
        LOGGER.debug(f'resulting speech: {speech}')
        return speech
