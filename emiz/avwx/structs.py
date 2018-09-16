"""
Contains dataclasses to hold report data
"""
# pylint: disable=all
import typing
from datetime import datetime

# stdlib
from dataclasses import dataclass


@dataclass
class StationInfo:
    city: str
    country: str
    elevation: float
    iata: str
    icao: str
    latitude: float
    longitude: float
    name: str
    priority: int
    state: str


@dataclass
class Units(object):
    altimeter: str
    altitude: str
    temperature: str
    visibility: str
    wind_speed: str


@dataclass
class Number(object):
    repr: str
    value: float
    spoken: str


@dataclass
class Fraction(Number):
    numerator: int
    denominator: int
    normalized: str


@dataclass
class Timestamp(object):
    repr: str
    dt: datetime


@dataclass
class Cloud(object):
    repr: str
    type: str
    altitude: int
    modifier: str = None  # type: ignore


@dataclass
class RemarksData(object):
    dewpoint_decimal: float = None  # type: ignore
    temperature_decimal: float = None  # type: ignore


@dataclass
class ReportData(object):
    raw: str
    remarks: str
    station: str
    time: Timestamp


@dataclass
class SharedData(object):
    altimeter: Number
    clouds: typing.List[Cloud]  # type: ignore
    flight_rules: str
    other: typing.List[str]  # type: ignore
    sanitized: str
    visibility: Number
    wind_direction: Number
    wind_gust: Number
    wind_speed: Number


@dataclass
class MetarData(ReportData, SharedData):
    dewpoint: Number
    remarks_info: RemarksData
    runway_visibility: typing.List[str]  # type: ignore
    temperature: Number
    wind_variable_direction: [Number]  # type: ignore


@dataclass
class TafLineData(SharedData):
    end_time: Timestamp
    icing: typing.List[str]  # type: ignore
    probability: Number
    raw: str
    start_time: Timestamp
    turbulance: typing.List[str]  # type: ignore
    type: str
    wind_shear: str


@dataclass
class TafData(ReportData):
    forecast: typing.List[TafLineData]  # noqa
    start_time: Timestamp
    end_time: Timestamp
    max_temp = None  # type: ignore
    min_temp = None  # type: ignore
    alts = None  # type: ignore
    temps = None  # type: ignore


@dataclass
class ReportTrans(object):
    altimeter: str
    clouds: str
    other: str
    visibility: str


@dataclass
class MetarTrans(ReportTrans):
    dewpoint: str
    remarks: dict
    temperature: str
    wind: str


@dataclass
class TafLineTrans(ReportTrans):
    icing: str
    turbulance: str
    wind: str
    wind_shear: str


@dataclass
class TafTrans(object):
    forecast: typing.List[TafLineTrans]  # noqa
    max_temp: str
    min_temp: str
    remarks: dict
