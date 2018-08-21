# coding=utf-8
"""
Access to AVWX API

https://avwx.rest/documentation
"""

import json

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
    def _failed_request(req: requests.Response, url: str):
        if req.reason == 'BAD REQUEST':
            _json = req.json()
            if 'Error' in _json:
                if 'Station Lookup Error: METAR not found for ' in _json['Error']:
                    station = _json['Error'].replace(
                        'Station Lookup Error: METAR not found for ', ''
                    ).replace('. There might not be a current report in ADDS', '')
                    raise StationNotFound(station)
        msg = f'failed to retrieve: {url}'
        LOGGER.error(msg)
        raise ConnectionError(msg)

    @staticmethod
    def _query(url, params: dict = None) -> AVWXResult:
        LOGGER.debug(f'querying: {url}{params}')
        req = AVWX.s.get(url, timeout=2, params=params, verify=certifi.where())
        if not req.ok:
            AVWX._failed_request(req, url)
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
        try:
            return AVWX._query(f'https://avwx.rest/api/metar/{icao}', params=params)
        except RequestsConnectionError:
            raise AVWXRequestFailedError('failed to obtain requested data from AVWX')

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
        speech = str(result.speech).replace('Altimeter', 'Q N H')
        LOGGER.debug(f'resulting speech: {speech}')
        return speech
