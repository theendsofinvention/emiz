# coding=utf-8
"""
Stupid class I wrote a while back to validate values (dummy me)
"""
from os.path import exists
from re import fullmatch as re_full_match


# pylint: disable=too-many-instance-attributes
class Validator:
    """Validates many kind of values against pre-defined conditions, raises Exception and logs errors"""

    def __init__(
            self,
            *,
            _type=None,
            _instance=None,
            _min=None,
            _max=None,
            _regex=None,
            _in_list=None,
            _path_exists=False,
            exc=None,
            logger=None
    ):
        self.type = _type
        self.instance = _instance
        self.min = _min
        self.max = _max
        self.regex = _regex
        self.in_list = _in_list
        self.path_exists = _path_exists
        self.exc = exc or ValueError
        self.logger = logger

    def validate(self, value, param_name, exc=None, logger=None):
        """
        :param value: value to validate
        :param param_name: name of the value (for logging purpose)
        :param exc: exception to raise (default is "ValidatorError")
        :param logger: logger to use (default will be "Validator.logger")
        """
        if exc is not None:
            self.exc = exc

        if logger is not None:
            self.logger = logger

        if self.type is not None and not type(value) == self.type:  # pylint: disable=unidiomatic-typecheck
            self.error(
                f'invalid type for parameter "{param_name}": {type(value)} (value: {value}) -- expected {self.type}'
            )

        if self.instance is not None and not isinstance(value, self.instance):
            self.error(
                f'invalid instance for parameter "{param_name}": {type(value)} (value: {value})'
                f' -- expected {self.instance}'
            )

        if self.min is not None and value < self.min:
            self.error(f'invalid value for parameter "{param_name}" (under minima of {self.min}): {value}')

        if self.max is not None and value > self.max:
            self.error(f'invalid value for parameter "{param_name}" (over maxima if {self.max}): {value}')

        if self.regex is not None and not re_full_match(self.regex, value):
            self.error(f'invalid value for parameter "{param_name}" (should match: "{self.regex}"): {value}')

        if self.in_list is not None and value not in self.in_list:
            self.error(f'invalid value for parameter "{param_name}"; "{value}" is not in list: {self.in_list}')

        if self.path_exists and not exists(value):
            self.error(f'"{param_name}" file does not exist: {value}')

        return True

    def error(self, error_msg):
        """
        Outputs error message on own logger. Also raises exceptions if need be.

        Args:
            error_msg: message to output

        """
        if self.logger is not None:
            self.logger.error(error_msg)

        if self.exc is not None:
            raise self.exc(error_msg)


VALID_BOOL = Validator(_type=bool)
VALID_STR = Validator(_type=str)
VALID_INT = Validator(_type=int)
VALID_POSITIVE_INT = Validator(_type=int, _min=0)
VALID_NEGATIVE_INT = Validator(_type=int, _max=0)
VALID_FLOAT = Validator(_type=float)
VALID_EXISTING_PATH = Validator(_path_exists=True)
VALID_LIST = Validator(_type=list)
VALID_DICT = Validator(_type=dict)
NOT_A_STR = [-1, True, False, None, 1234, dict(), list(), set(), tuple()]
NOT_AN_INT = [True, False, None, '', 'meh', 12.34, dict(), list(), set(), tuple()]
NOT_A_POSITIVE_INT = [True, False, None, '', 'meh', 12.34, -1, -100000, dict(), list(), set(), tuple()]
NOT_A_BOOL = [None, 1, 12.34, 'meh', dict(), list(), set(), tuple()]
