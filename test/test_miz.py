# coding=utf-8

import os
from pathlib import Path

import pytest

from emiz.mission import Mission
from emiz.miz import Miz


@pytest.mark.parametrize('cls', [Miz])
def test_init(tmpdir, cls):
    t = Path(str(tmpdir))

    f = t.joinpath('f.txt')

    with pytest.raises(FileNotFoundError):
        cls(f)

    with pytest.raises(TypeError):
        cls(t)

    f.write_text('')

    with pytest.raises(ValueError):
        cls(f)

    f = t.joinpath('f.miz')
    f.write_text('')

    cls(f)


def test_unzip(test_file):
    m = Miz(test_file)
    m.unzip()


def test_context(test_file):
    with Miz(test_file) as miz:
        assert isinstance(miz.mission, Mission)
        tmpdir = os.path.abspath(miz.temp_dir)

    assert not os.path.exists(tmpdir)
