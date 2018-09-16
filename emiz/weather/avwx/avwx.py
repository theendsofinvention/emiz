# coding=utf-8
"""
Access to AVWX API

https://avwx.rest/documentation
"""

import elib
import emiz.avwx.metar
import emiz.avwx.speech

LOGGER = elib.custom_logging.get_logger('EMIZ')


# pylint: disable=too-few-public-methods
class AVWX:
    """
    Using vendored AVWX engine
    """

    @staticmethod
    def metar_to_speech(metar: str) -> str:
        """
        Creates a speakable text from a METAR

        Args:
            metar: METAR string to use

        Returns: speakable METAR for TTS

        """
        LOGGER.info('getting speech text from METAR: %s', metar)
        metar_data, metar_units = emiz.avwx.metar.parse_in(metar)
        speech = emiz.avwx.speech.metar(metar_data, metar_units)
        speech = str(speech).replace('Altimeter', 'Q N H')
        LOGGER.debug('resulting speech: %s', speech)
        return speech
