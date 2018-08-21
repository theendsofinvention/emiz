# coding=utf-8
"""
AWC exceptions
"""


class AWCException(Exception):
    """Base AWC exception"""


class InvalidICAO(AWCException):
    """Raised when the given ICAO is invalid"""


class AWCRequestFailed(AWCException):
    """Raised when the request failed (generic error)"""

    def __init__(self, icao: str) -> None:
        super(AWCRequestFailed, self).__init__(f'request failed for ICAO "{icao}"')


class NoMetarForStation(AWCException):
    """Raised when no METAR was found for station"""

    def __init__(self, icao: str) -> None:
        super(NoMetarForStation, self).__init__(
            f'no METAR found for station: "{icao}"; you might want to try another ICAO code.\n'
            f'A complete list of available stations can be found at '
            f'https://www.aviationweather.gov/docs/metar/stations.txt'
        )
