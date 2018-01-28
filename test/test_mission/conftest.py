# coding=utf-8
"""
Configuration test specific to Mission & Miz
"""

import copy
from pathlib import Path

import pytest

from emiz import Mission, Miz

TEST_FILES_FOLDER = Path('./test/test_files').absolute()
if not TEST_FILES_FOLDER.exists():
    raise RuntimeError('cannot find test files')


@pytest.fixture(
    params=[
        Path(TEST_FILES_FOLDER.joinpath('TRG_KA50.miz')),
        Path(TEST_FILES_FOLDER.joinpath('test_158.miz')),
    ],
    ids=['older version', '1.5.8']
)
def test_file(request):
    yield request.param


@pytest.fixture()
def out_file():
    yield Path(TEST_FILES_FOLDER.joinpath('TRG_KA50_EMFT.miz'))


@pytest.fixture()
def bad_zip_file():
    yield Path(TEST_FILES_FOLDER.joinpath('bad_zip_file.miz'))


@pytest.fixture()
def missing_file():
    yield Path(TEST_FILES_FOLDER.joinpath('missing_files.miz'))


@pytest.fixture()
def duplicate_group_id():
    yield Path(TEST_FILES_FOLDER.joinpath('duplicate_group_id.miz'))


@pytest.fixture()
def all_objects():
    yield Path(TEST_FILES_FOLDER.joinpath('all_objects.miz'))


@pytest.fixture()
def large_file():
    yield Path(TEST_FILES_FOLDER.joinpath('TRMT_2.4.0.miz'))


@pytest.fixture()
def radio_file():
    yield Path(TEST_FILES_FOLDER.joinpath('radios.miz'))


@pytest.fixture()
def bad_files():
    yield ['bad_zip_file.miz', 'missing_files.miz']


@pytest.fixture(autouse=True)
def remove_out_file():
    """Removes OUT_FILE between tests"""
    path = Path(TEST_FILES_FOLDER.joinpath('TRG_KA50_EMFT.miz'))
    if path.exists():
        path.unlink()
    yield
    if path.exists():
        path.unlink()


with Miz(Path(TEST_FILES_FOLDER.joinpath('test_158.miz'))) as miz:
    DUMMY_MISSION = miz.mission


@pytest.fixture(scope='function')
def mission():
    yield Mission(copy.deepcopy(DUMMY_MISSION.d), copy.deepcopy(DUMMY_MISSION.l10n))


@pytest.fixture()
def mission_dict():
    yield copy.deepcopy(DUMMY_MISSION.d)


@pytest.fixture()
def mission_l10n():
    yield copy.deepcopy(DUMMY_MISSION.l10n)
