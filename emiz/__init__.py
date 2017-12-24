# coding=utf-8
"""
Etcher's MIZ library
"""

from emiz.edit_miz import edit_miz
from emiz.weather import build_metar_from_mission
from emiz.weather.utils import parse_metar_string, retrieve_metar
from ._e_version import get_versions
from .miz import Mission, Miz
from .parking_spots import parkings
from elib.custom_logging import get_logger

__all__ = ['parse_metar_string', 'retrieve_metar', 'Miz', 'Mission', 'edit_miz', 'build_metar_from_mission']

__version__ = get_versions()['version']
del get_versions


MAIN_LOGGER = get_logger('EMIZ')
