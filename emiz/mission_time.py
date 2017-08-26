# coding=utf-8

import datetime
import logging
import re

from emiz.miz import Miz

LOGGER = logging.getLogger('EMIZ').getChild(__name__)

RE_INPUT_STRING = re.compile(r'^'
                             r'(?P<year>[\d]{4})'
                             r'(?P<month>[\d]{2})'
                             r'(?P<day>[\d]{2})'
                             r'(?P<hour>[\d]{2})'
                             r'(?P<minute>[\d]{2})'
                             r'(?P<second>[\d]{2})'
                             r'$')


class MissionTime:
    def __init__(self, moment: datetime.datetime):
        self.date = datetime.date(moment.year, moment.month, moment.day)
        self.time = moment.hour * 3600 + moment.minute * 60 + moment.second

    def apply_to_miz(self, miz):
        miz.mission.day = self.date.day
        miz.mission.month = self.date.month
        miz.mission.year = self.date.year
        miz.mission.mission_start_time = self.time

        return True

    @staticmethod
    def from_string(input_str):
        match = RE_INPUT_STRING.match(input_str)
        if not match:
            raise ValueError(f'badly formatted date/time: {input_str}')

        return MissionTime(
            datetime.datetime(
                int(match.group('year')),
                int(match.group('month')),
                int(match.group('day')),
                int(match.group('hour')),
                int(match.group('minute')),
                int(match.group('second')),
            )
        )

    @staticmethod
    def now():
        return MissionTime(datetime.datetime.now())
