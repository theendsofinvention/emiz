# coding=utf-8
"""
Access to AVWX API

https://avwx.rest/documentation
"""

import json
from collections import namedtuple

import requests
import requests.adapters

from emiz import MAIN_LOGGER

LOGGER = MAIN_LOGGER.getChild(__name__)


AVWXResult = namedtuple('AVWXResult', 'Meta, Altimeter, CloudList, Dewpoint, FlightRules, Info, OtherList, RawReport,'
                                      'Remarks, RemarksInfo, RunwayVisList, Speech, Station, Summary, Temperature,'
                                      'Time, Units, Visibility, WindDirection, WindGust, WindSpeed,'
                                      'WindVariableDir,City, Country, Elevation, IATA, ICAO, Latitude,'
                                      'Longitude, Name, Priority, State')


# pylint: disable=too-few-public-methods
class AVWX:
    """
    Access to AVWX API

    https://avwx.rest/documentation
    """
    s = requests.Session()
    s.mount('https://avwx.rest', requests.adapters.HTTPAdapter(max_retries=10))

    @staticmethod
    def _query(url) -> dict:
        LOGGER.debug(f'querying: {url}')
        req = AVWX.s.get(url, timeout=2)
        if not req.ok:
            raise ConnectionError(f'failed to retrieve: {url}')
        return json.loads(req.content)

    @staticmethod
    def query_icao(icao: str) -> AVWXResult:
        """
        Queries AVWX API for weather at given station

        Args:
            icao: ICAO code of the station

        Returns: AVWXResult instance

        """
        data = AVWX._query(f'https://avwx.rest/api/metar/{icao}?options=info,speech,summary')
        for key in data:
            if '-' in key:
                new_key = str(key).replace('-', '')
                data[new_key] = data[key]
                del data[key]
        try:
            data.update(data['Info'])
        except KeyError:
            import pprint
            LOGGER.error(f'data is missing "Info":\n{pprint.pformat(data)}')
            raise
        try:
            return AVWXResult(**data)
        except TypeError:
            import pprint
            LOGGER.error(f'invalid data was:\n{pprint.pformat(data)}')
            raise
