# coding=utf-8
"""
Wrappers around https://aviationweather.gov/ services
"""

import certifi
import elib
import requests.adapters
from requests import ConnectionError as RequestsConnectionError

from emiz.weather.awc.awc_result import AWCResult
from emiz.weather.awc.exc import AWCRequestFailed, InvalidICAO

LOGGER = elib.custom_logging.get_logger('EMIZ')


class AWC:
    """
    Dummy container for all first-class methods related to AWC
    """
    s = requests.Session()
    s.mount(
        'https://aviationweather.gov/adds/dataserver_current/httpparam',
        requests.adapters.HTTPAdapter(max_retries=3),
    )

    @staticmethod
    def _validate_icao(icao: str):
        """Checks ICAO"""
        if len(icao) != 4:
            raise InvalidICAO(icao)

    @staticmethod
    def _query(params: dict) -> AWCResult:
        # LOGGER.debug(f'querying: {url}{params}')
        LOGGER.debug('requesting METAR for station: %s', params["stationString"])
        req = AWC.s.get(
            url='https://aviationweather.gov/adds/dataserver_current/httpparam',
            timeout=2, params=params, verify=certifi.where()
        )
        if req.ok:
            response = req.content.decode('utf8').splitlines()
            return AWCResult(params['stationString'], response)

        raise AWCRequestFailed(params['stationString'])

    @staticmethod
    def query_icao(icao: str):
        """
        Queries AWC for the METAR of a given station

        Args:
            icao: station ID as a four letters-digits ICAO code

        Returns: AWC result for the station

        """
        params = {
            'dataSource': 'metars',
            'requestType': 'retrieve',
            'format': 'csv',
            'hoursBeforeNow': 24,
        }
        AWC._validate_icao(icao)
        params['stationString'] = icao
        try:
            return AWC._query(params)
        except RequestsConnectionError:
            raise AWCRequestFailed('failed to obtain requested data from AWC')
