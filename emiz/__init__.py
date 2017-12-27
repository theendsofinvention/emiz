# coding=utf-8
# pylint: disable=wrong-import-position
"""
Etcher's MIZ library
"""
from elib.custom_logging import get_logger

from ._e_version import get_versions

__version__ = get_versions()['version']
del get_versions

MAIN_LOGGER = get_logger('EMIZ')
MAIN_LOGGER.info(f'EMIZ version {__version__}')

from emiz.edit_miz import edit_miz
from .miz import Mission, Miz
from .parking_spots import parkings
from . import weather

__all__ = ['Miz', 'Mission', 'edit_miz', 'weather']
