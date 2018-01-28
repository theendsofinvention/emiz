# coding=utf-8
# pylint: disable=wrong-import-position
"""
Etcher's MIZ library
"""
from elib.custom_logging import get_logger
from pkg_resources import DistributionNotFound, get_distribution

try:
    __version__ = get_distribution('epab').version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = 'not installed'

MAIN_LOGGER = get_logger('EMIZ')
MAIN_LOGGER.info(f'EMIZ version {__version__}')

from . import weather, edit_miz
from .miz import Mission, Miz

__all__ = ['Miz', 'Mission', 'edit_miz', 'weather']
