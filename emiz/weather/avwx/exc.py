# coding=utf-8
"""
Exceptions for AVWX package
"""


class AVWXError(Exception):
    """Base AVWX exception"""


class AVWXRequestFailedError(AVWXError):
    """Raised when request failed"""


class StationNotFound(AVWXError):
    """
    Raised when a ICAO station isn't found
    """

    def __init__(self, icao: str) -> None:
        msg = f'ICAO station not found on AVWX server: "{icao}"; you might want to try another one.'
        super(StationNotFound, self).__init__(msg)
