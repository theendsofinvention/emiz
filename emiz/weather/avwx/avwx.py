# coding=utf-8
"""
Access to AVWX API

https://avwx.rest/documentation
"""

import json

import requests
import requests.adapters

from emiz import MAIN_LOGGER

from .avwx_result import AVWXResult

LOGGER = MAIN_LOGGER.getChild(__name__)


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
        LOGGER.debug(f'querying: {url}{params}')
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
        speech = str(result.speech).replace('Altimeter', 'Q N H')
        LOGGER.debug(f'resulting speech: {speech}')
        return speech
