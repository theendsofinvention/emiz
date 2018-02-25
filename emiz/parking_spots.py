# coding=utf-8
"""
Artifact from earlier dev
"""

import math
import pickle
from collections import namedtuple

# pylint: skip-file
# noinspection PyProtectedMember
from emiz._parking_spots import parkings
from emiz.mission import Static

ParkingSpot = namedtuple('ParkingSpot', 'airport spot')
parkings = pickle.loads(parkings)


def clear_farps():
    """
    Removes all FARPs
    """
    parkings['FARP'] = {}


def add_farp(farp: Static):
    """
    Adds a FARP

    Args:
        farp: FARP object to add
    """
    parkings['FARP'][farp.static_name] = farp.static_position


def unit_pos_to_spot(unit_pos) -> ParkingSpot:
    """
    Translates a unit position to a known parking spot

    Args:
        unit_pos: unit position as Vec2

    Returns: ParkingSpot object

    """
    min_ = 50
    res = None
    for airport in parkings:
        for spot in parkings[airport]:
            spot_pos = parkings[airport][spot]
            dist = math.hypot(unit_pos[0] - spot_pos[0], unit_pos[1] - spot_pos[1])
            if dist < min_:
                min_ = dist
                res = ParkingSpot(airport=airport, spot=spot)
    return res
