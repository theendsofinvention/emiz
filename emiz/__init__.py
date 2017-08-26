# coding=utf-8

from pkg_resources import DistributionNotFound, get_distribution

from .miz import Mission, Miz
from .parking_spots import parkings
from emiz.weather.utils import retrieve_metar, parse_metar_string
from emiz.weather import build_metar_from_mission
from emiz.edit_miz import edit_miz

try:
    __version__ = get_distribution('emiz').version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = 'not installed'

__all__ = ['parse_metar_string', 'retrieve_metar', 'Miz', 'Mission', 'edit_miz', 'build_metar_from_mission']
