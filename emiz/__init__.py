# coding=utf-8
# pylint: disable=wrong-import-position
"""
Etcher's MIZ library
"""
from pkg_resources import DistributionNotFound, get_distribution

try:
    __version__ = get_distribution('emiz').version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = 'not installed'

from . import weather, edit_miz
from .miz import Mission, Miz

__all__ = ['Miz', 'Mission', 'edit_miz', 'weather']
