# coding=utf-8

import os

import datadiff
import pytest

from emiz.miz import ENCODING
from emiz.sltp import SLTP, SLTPParsingError


def _assert_same(input_, output):

    for x in input_:
        try:
            assert x in output
        except AssertionError:
            print(datadiff.diff(input_, output))
            raise

    assert len(input_) == len(output)


def _assert_different(input_, output):

    for x in input_:
        try:
            assert x in output
        except AssertionError:
            break
    else:
        pytest.fail('resulting dicts should be different')


def _do_test(test_file, compare_func):
    parser = SLTP()
    with open(test_file, encoding=ENCODING) as f:
        data = f.read()
    decoded_data, qualifier = parser.decode(data)

    parser = SLTP()
    encoded_data = parser.encode(decoded_data, qualifier)

    output = encoded_data.split('\n')
    input_ = data.split('\n')

    compare_func(input_, output)


def test_encode_decode_files(sltp_pass):
    _do_test(sltp_pass, _assert_same)


@pytest.mark.long
def test_encode_decode_files_long(sltp_long):
    _do_test(sltp_long, _assert_same)


def test_encode_decode_files_fail(sltp_fail):
    with pytest.raises(SLTPParsingError):
        _do_test(sltp_fail, _assert_same)


def test_encode_decode_files_diff(sltp_diff):
    _do_test(sltp_diff, _assert_different)
