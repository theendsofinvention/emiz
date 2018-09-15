# coding=utf-8
"""
Access to AVWX API

https://avwx.rest/documentation
"""

import certifi
import elib
import requests.adapters
from requests.exceptions import ConnectionError as RequestsConnectionError

from emiz.weather.avwx.avwx_result import AVWXResult
from emiz.weather.avwx.exc import AVWXRequestFailedError, StationNotFound

LOGGER = elib.custom_logging.get_logger('EMIZ')


# pylint: disable=too-few-public-methods
class AVWX:
    """
    Access to AVWX API

    https://avwx.rest/documentation
    """
    s = requests.Session()
    s.mount('https://avwx.rest', requests.adapters.HTTPAdapter(max_retries=3))

    @staticmethod
    def _failed_request(req: requests.Response, url: str, icao: str):
        if req.reason == 'BAD REQUEST':
            _json = req.json()
            if 'Error' in _json:
                if _json['Error'] == 'No report or cache was found for the requested station':
                    raise StationNotFound(icao)
        msg = f'failed to retrieve: {url}'
        LOGGER.error(msg)
        raise ConnectionError(msg)

    @staticmethod
    def _sanitize_result(data: dict) -> dict:
        result = {}
        LOGGER.debug('sanitizing data keys')
        for key in data:
            new_key = str(key).replace('-', '')
            new_key = new_key.lower()
            result[new_key] = data[key]
        return result

    @staticmethod
    def _query(url, icao: str, params: dict = None) -> AVWXResult:
        LOGGER.debug('querying: %s %s', url, params)
        req = AVWX.s.get(url, timeout=2, params=params, verify=certifi.where())
        if not req.ok:
            AVWX._failed_request(req, url, icao)
        LOGGER.debug('parsing data')
        result = AVWX._sanitize_result(req.json())
        try:
            LOGGER.debug('returning AVWXResult instance')
            return AVWXResult(**result)
        except TypeError:
            import pprint
            LOGGER.error('invalid data was:\n%s', pprint.pformat(result))
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
            'options': 'info,speech,summary,translate',
            'format': 'json',
            'onfail': 'cache',
        }
        LOGGER.info('getting METAR info for ICAO: %s', icao)
        try:
            return AVWX._query(f'https://avwx.rest/api/metar/{icao}', params=params, icao=icao)
        except RequestsConnectionError:
            raise AVWXRequestFailedError('failed to obtain requested data from AVWX')

    @staticmethod
    def _post(url: str, body: str, params: dict) -> str:
        LOGGER.debug('posting request for METAR parsing')
        resp = AVWX.s.post(url=url, data=body.encode('utf8'), params=params)
        if not resp.ok:
            LOGGER.error('post request failed')
            AVWX._failed_request(resp, url, 'none')
        LOGGER.debug('post request success')
        result = AVWX._sanitize_result(resp.json())
        return result['speech']

    @staticmethod
    def metar_to_speech(metar: str) -> str:
        """
        Creates a speakable text from a METAR

        Args:
            metar: METAR string to use

        Returns: speakable METAR for TTS

        """
        LOGGER.info('getting speech text from METAR: %s', metar)
        params = {
            'options': 'info,speech,summary'
        }
        speech = AVWX._post(
            url='http://avwx.rest/api/metar/parse',
            body=metar,
            params=params
        )
        speech = str(speech).replace('Altimeter', 'Q N H')
        LOGGER.debug('resulting speech: %s', speech)
        return speech
