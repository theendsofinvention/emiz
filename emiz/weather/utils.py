# coding=utf-8
"""
Utility function for weather
"""

from emiz import MAIN_LOGGER

LOGGER = MAIN_LOGGER.getChild(__name__)


# noinspection SpellCheckingInspection
def hpa_to_mmhg(pressure: int) -> int:
    """
    Converts pressure in hpa to mmhg
    Args:
        pressure: pressure to convert

    Returns: pressure in mmhg

    """
    return int(pressure * 0.75006156130264)


def reverse_direction(heading: int) -> int:
    """
    Inverts a direction in degrees

    Args:
        heading: original direction

    Returns: direction plus or minus 180°

    """
    if heading >= 180:
        return int(heading - 180)

    return int(heading + 180)
