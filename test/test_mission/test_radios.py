# coding=utf-8
"""
Tests radio
"""
import pytest

from emiz import Miz
from emiz.mission import FlyingUnit

RADIOS_TESTS = [
    (
        1, 'F-86F Sabre',
        [
            ('ARC-27', 1, {
                1: 225.0, 2: 225.0, 3: 399.9, 4: 270.2, 5: 255.0, 6: 259.0, 7: 262.0, 8: 257.0, 9: 253.2, 10: 263.0,
                11: 267.0, 12: 254.0, 13: 264.0, 14: 266.0, 15: 265.0, 16: 252.0, 17: 268.0, 18: 269.0},),
            ('ARC-27', 1, {
                1: 225.0, 2: 225.0, 3: 399.9, 4: 270.2, 5: 255.0, 6: 259.0, 7: 262.0, 8: 257.0, 9: 253.2, 10: 263.0,
                11: 267.0, 12: 254.0, 13: 264.0, 14: 266.0, 15: 265.0, 16: 252.0, 17: 268.0, 18: 269.0},),
        ]
    ),
    (
        2, 'M-2000C',
        [
            ('UHF', 1, {
                1: 225.0, 2: 400.0, 3: 225.0, 4: 256.3, 5: 254.0, 6: 250.0, 7: 270.0, 8: 257.0, 9: 255.0, 10: 262.0,
                11: 259.0, 12: 268.0, 13: 269.0, 14: 260.0, 15: 263.0, 16: 261.0, 17: 267.0, 18: 251.0, 19: 253.0,
                20: 266.0},),
            ('V/UHF', 2, {
                1: 129.2, 2: 118.0, 3: 400.0, 4: 127.0, 5: 125.0, 6: 121.0, 7: 141.0, 8: 128.0, 9: 126.0, 10: 133.0,
                11: 130.0, 12: 139.0, 13: 140.0, 14: 131.0, 15: 134.0, 16: 132.0, 17: 138.0, 18: 122.0, 19: 124.0,
                20: 137.0},),
        ]
    ),
    (
        3, 'MiG-21Bis',
        [
            ('R-832', 1, {
                1: 120.0, 2: 80.0, 3: 399.9, 4: 121.25, 5: 125.222, 6: 126.0, 7: 130.0, 8: 133.0, 9: 122.0, 10: 124.0,
                11: 134.0, 12: 125.0, 13: 135.0, 14: 137.0, 15: 136.0, 16: 123.0, 17: 132.0, 18: 127.0, 19: 129.0,
                20: 138.0},),
        ]
    ),
    (
        4, 'P-51D',
        [
            ('SCR552', 1, {1: 124.0, 2: 100.0, 3: 156.0, 4: 139.0},),
        ]
    ),
    (
        5, 'TF-51D',
        [
            ('SCR552', 1, {1: 124.0, 2: 124.0, 3: 131.0, 4: 139.0},),
        ]
    ),
    (
        6, 'Ka-50',
        [
            ('R828', 1, {
                1: 21.5, 2: 20.0, 3: 59.9, 4: 28.0, 5: 30.0, 6: 32.0, 7: 40.0, 8: 50.0, 9: 55.5, 10: 59.9},),
            ('ARK22', 2, {
                1: 0.625, 2: 0.15, 3: 1.75, 4: 0.591, 5: 0.408, 6: 0.803, 7: 0.443, 8: 0.215, 9: 0.525, 10: 1.065,
                11: 0.718, 12: 0.35, 13: 0.583, 14: 0.283, 15: 0.995, 16: 1.21},),
        ]
    ),
    (
        7, 'Mi-8MT',
        [
            ('R863', 1, {
                1: 127.5, 2: 100.0, 3: 399.9, 4: 127.0, 5: 125.0, 6: 121.0, 7: 141.0, 8: 128.0, 9: 126.0, 10: 133.0,
                11: 130.0, 12: 129.0, 13: 123.0, 14: 131.0, 15: 134.0, 16: 132.0, 17: 138.0, 18: 122.0, 19: 124.0,
                20: 137.0},),
            ('R828', 2, {
                1: 21.5, 2: 20.0, 3: 59.9, 4: 28.0, 5: 30.0, 6: 32.0, 7: 40.0, 8: 50.0, 9: 55.5, 10: 59.9},),
        ]
    ),
    (
        8, 'UH-1H',
        [
            ('ARC51', 1, {
                1: 251.0, 2: 225.0, 3: 399.975, 4: 256.0, 5: 254.0, 6: 250.0, 7: 270.0, 8: 257.0, 9: 255.0, 10: 262.0,
                11: 259.0, 12: 268.0, 13: 269.0, 14: 260.0, 15: 263.0, 16: 261.0, 17: 267.0, 18: 251.0, 19: 253.0,
                20: 266.0},),
        ]
    ),
]


@pytest.mark.parametrize('unit_id, unit_type, radios_to_test', RADIOS_TESTS)
def test_radios(unit_id, unit_type, radios_to_test, radio_file):
    with Miz(radio_file) as miz:
        mission = miz.mission

    unit = mission.get_unit_by_id(unit_id)
    assert unit.unit_type == unit_type
    assert isinstance(unit, FlyingUnit)
    for radio in radios_to_test:
        radio_name, radio_number, channels_to_test = radio
        radio_by_name = unit.get_radio_by_name(radio_name)
        radio_by_number = unit.get_radio_by_number(radio_number)
        assert radio_by_name == radio_by_number
        for channel, freq in channels_to_test.items():
            assert radio_by_name.get_frequency(channel) == freq
            assert radio_by_number.get_frequency(channel) == freq


def test_radios_set_freq(radio_file, out_file):
    with Miz(radio_file) as miz:
        unit = miz.mission.get_unit_by_id(1)
        assert isinstance(unit, FlyingUnit)
        radio = unit.get_radio_by_number(1)
        radio.set_frequency(1, radio.min)
        radio.set_frequency(1, radio.max)
        for wrong_freq_type in [None, False, True, 'caribou', 0, -1]:
            with pytest.raises(ValueError):
                radio.set_frequency(1, wrong_freq_type)
        for wrong_freq in [radio.max + 1, radio.min - 1]:
            with pytest.raises(ValueError):
                radio.set_frequency(1, wrong_freq)
        miz.zip(out_file)
        with Miz(out_file) as miz2:
            unit2 = miz2.mission.get_unit_by_id(1)
            assert isinstance(unit2, FlyingUnit)
            radio2 = unit2.get_radio_by_number(1)
            assert type(radio) == type(radio2)


def test_radios_equal(radio_file):
    with Miz(radio_file) as miz:
        unit = miz.mission.get_unit_by_id(6)
        assert isinstance(unit, FlyingUnit)
        radio1 = unit.get_radio_by_number(1)
        radio2 = unit.get_radio_by_number(2)
        assert not radio1 == radio2
        radio3 = miz.mission.get_unit_by_id(7).get_radio_by_number(2)
        assert radio1.radio_name == radio3.radio_name
        assert radio1 == radio3
        radio1.set_frequency(1, 30.0)
        assert not radio1 == radio3


def test_radios_generator(radio_file):
    with Miz(radio_file) as miz:
        unit = miz.mission.get_unit_by_id(6)
        # noinspection PyUnusedLocal
        for radio in unit.radio_presets:
            # TODO resume
            pass
