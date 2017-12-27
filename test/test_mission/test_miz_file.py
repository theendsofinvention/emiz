# coding=utf-8
"""
Test MIZ functionality
"""
import pytest

from emiz.mission import Mission
from emiz.miz import Miz


def test_init(test_file):
    Miz(test_file)
    with pytest.raises(FileNotFoundError):
        Miz('./i_do_not_exist')


def test_context(test_file):
    with Miz(test_file) as miz:
        assert isinstance(miz.mission, Mission)
        assert isinstance(miz.l10n, dict)
        assert miz.zip_content


def test_unzip(test_file):
    miz = Miz(test_file)
    miz.unzip()


def test_decode(test_file):
    miz = Miz(test_file)
    miz.unzip()
    miz.decode()


def test_zip(out_file, test_file):
    assert not out_file.exists()
    with Miz(test_file) as miz:
        miz.zip(out_file)
    assert out_file.exists()
    with Miz(out_file) as miz2:
        assert miz.mission.d == miz2.mission.d
        miz.mission.weather.cloud_density = 4
        assert not miz.mission.d == miz2.mission.d


def test_is_unzipped(test_file):
    mis = Miz(test_file)
    assert not mis.zip_content
    mis.unzip()
    assert mis.zip_content


def test_missing_file_in_miz(missing_file):
    missing = Miz(missing_file)
    with pytest.raises(FileNotFoundError):
        missing.unzip()


def test_bad_zip_file(bad_zip_file):
    from zipfile import BadZipFile
    mis = Miz(bad_zip_file)
    with pytest.raises(BadZipFile):
        mis.unzip()


def test_temp_dir_cleaning(test_file):
    mis = Miz(test_file)
    mis.unzip()
    assert mis.temp_dir.exists()
    assert mis.temp_dir.glob('*')
    mis._remove_temp_dir()
    assert not mis.temp_dir.exists()
