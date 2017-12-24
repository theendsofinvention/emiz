# coding=utf-8
# pylint: disable=wrong-import-position
"""
Etcher's MIZ library
"""
from elib.custom_logging import get_logger
from emiz._e_version import get_versions

__version__ = get_versions()['version']
del get_versions

MAIN_LOGGER = get_logger('EMIZ')
MAIN_LOGGER.info(f'EMIZ version {__version__}')

from emiz.edit_miz import edit_miz
from emiz.weather import build_metar_from_mission
from emiz.weather.utils import parse_metar_string, retrieve_metar
from .miz import Mission, Miz
from .parking_spots import parkings

__all__ = ['parse_metar_string', 'retrieve_metar', 'Miz', 'Mission', 'edit_miz', 'build_metar_from_mission']
