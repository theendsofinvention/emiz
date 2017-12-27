# coding=utf-8
"""
Long tests running on large files
"""

from pathlib import Path
from time import sleep

import pytest

from emiz.miz import ENCODING, Miz


@pytest.mark.long
def test_large_decode(large_file):
    miz = Miz(large_file)
    miz.unzip()
    miz.decode()


@pytest.mark.long
def test_large_zip(large_file):
    with Miz(large_file, keep_temp_dir=True) as miz:
        out_file = miz.zip()
    assert Path(out_file).exists()
    try:
        with Miz(out_file) as miz2:
            assert miz.mission.d == miz2.mission.d
            miz.mission.weather.cloud_density = 4
            assert not miz.mission.d == miz2.mission.d
            sleep(1)
            m1 = miz.mission_file
            m2 = miz2.mission_file
            with open(m1, encoding=ENCODING) as _f:
                t1 = _f.read()
            with open(m2, encoding=ENCODING) as _f:
                t2 = _f.read()
            assert t1 == t2
    finally:
        Path(out_file).unlink()
