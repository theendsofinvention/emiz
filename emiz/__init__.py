# coding=utf-8
"""
Etcher's MIZ library
"""
from pkg_resources import DistributionNotFound, get_distribution

from emiz.edit_miz import edit_miz
from emiz.weather import build_metar_from_mission
from emiz.weather.utils import parse_metar_string, retrieve_metar
from .miz import Mission, Miz
from .parking_spots import parkings

try:
    __version__ = get_distribution('emiz').version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = 'not installed'

__all__ = ['parse_metar_string', 'retrieve_metar', 'Miz', 'Mission', 'edit_miz', 'build_metar_from_mission']
