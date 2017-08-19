# coding=utf-8
import tempfile
import os
import logging
from filecmp import dircmp
from os.path import exists, join
from zipfile import BadZipFile, ZipFile, ZipInfo
import shutil

from pathlib import Path

from emiz.sltp import SLTP
from emiz.mission import Mission
from emiz.dummy_miz import dummy_miz

LOGGER = logging.getLogger('EMIZ').getChild(__name__)
ENCODING = 'iso8859_15'


class Miz:
    def __init__(self, path_to_miz_file, temp_dir=None, keep_temp_dir: bool = False, overwrite: bool = False):

        self.miz_path = Path(path_to_miz_file)

        if not self.miz_path.exists():
            raise FileNotFoundError(path_to_miz_file)

        if not self.miz_path.is_file():
            raise TypeError(path_to_miz_file)

        if not self.miz_path.suffix == '.miz':
            raise ValueError(path_to_miz_file)

        if temp_dir is not None:
            raise PendingDeprecationWarning()

        self.keep_temp_dir = keep_temp_dir

        self.overwrite = overwrite

        self.tmpdir = Path(tempfile.mkdtemp('EMFT_'))
        LOGGER.debug('temporary directory: {}'.format(self.tmpdir.absolute()))

        self.zip_content = None
        self._mission = None
        self._mission_qual = None
        self._l10n = None
        self._l10n_qual = None
        self._map_res = None
        self._map_res_qual = None

    def __enter__(self):
        LOGGER.debug('instantiating new Mission object as a context')
        self.unzip(self.overwrite)
        self._decode()
        return self

    def __exit__(self, exc_type, exc_val, _):
        if exc_type:
            LOGGER.error('there were error with this mission, keeping temp dir at "{}" and re-raising'.format(
                self.tmpdir.absolute()))
            LOGGER.error('{}\n{}'.format(exc_type, exc_val))
            return False
        else:
            LOGGER.debug('closing Mission object context')
            if not self.keep_temp_dir:
                LOGGER.debug('removing temp dir: {}'.format(self.tmpdir.absolute()))
                self._remove_temp_dir()

    @property
    def mission_file(self):
        return self.tmpdir.joinpath('mission')

    @property
    def dictionary_file(self):
        return self.tmpdir.joinpath('l10n', 'DEFAULT', 'dictionary')

    @property
    def map_res_file(self):
        return self.tmpdir.joinpath('l10n', 'DEFAULT', 'mapResource')

    @property
    def mission(self) -> Mission:
        if self._mission is None:
            raise RuntimeError()
        return self._mission

    @property
    def l10n(self) -> dict:
        if self._l10n is None:
            raise RuntimeError()
        return self._l10n

    @property
    def map_res(self) -> dict:
        if self._map_res is None:
            raise RuntimeError()
        return self._map_res

    @staticmethod
    def reorder(miz_file_path, target_dir, skip_options_file):

        LOGGER.debug('re-ordering miz file: {}'.format(miz_file_path))
        LOGGER.debug('destination folder: {}'.format(target_dir))
        LOGGER.debug('{}option file'.format('skipping' if skip_options_file else 'including'))

        if not Path(target_dir).exists():
            LOGGER.debug(f'creating directory {target_dir}')
            os.makedirs(target_dir)

        with Miz(miz_file_path, overwrite=True) as m:

            def mirror_dir(src, dst):
                LOGGER.debug('{} -> {}'.format(src, dst))
                diff_ = dircmp(src, dst, ignore)
                diff_list = diff_.left_only + diff_.diff_files
                LOGGER.debug('differences: {}'.format(diff_list))
                for x in diff_list:
                    source = Path(diff_.left).joinpath(x)
                    target = Path(diff_.right).joinpath(x)
                    LOGGER.debug('looking at: {}'.format(x))
                    if source.is_dir():
                        LOGGER.debug('isdir: {}'.format(x))
                        if not target.exists():
                            LOGGER.debug('creating: {}'.format(x))
                            target.mkdir()
                        mirror_dir(source, target)
                    else:
                        LOGGER.debug('copying: {}'.format(x))
                        shutil.copy2(source.absolute(), diff_.right)
                for sub in diff_.subdirs.values():
                    assert isinstance(sub, dircmp)
                    mirror_dir(sub.left, sub.right)

            m._encode()

            if skip_options_file:
                ignore = ['options']
            else:
                ignore = []

            mirror_dir(m.tmpdir, target_dir)

    def _decode(self):

        LOGGER.debug('decoding lua tables')

        if not self.zip_content:
            self.unzip(overwrite=False)

        LOGGER.debug('reading map resource file')
        with open(self.map_res_file, encoding=ENCODING) as f:
            self._map_res, self._map_res_qual = SLTP().decode(f.read())

        LOGGER.debug('reading l10n file')
        with open(self.dictionary_file, encoding=ENCODING) as f:
            self._l10n, self._l10n_qual = SLTP().decode(f.read())

        LOGGER.debug('reading mission file')
        with open(self.mission_file, encoding=ENCODING) as f:
            mission_data, self._mission_qual = SLTP().decode(f.read())
            self._mission = Mission(mission_data, self._l10n)

        LOGGER.debug('decoding done')

    def _encode(self):

        LOGGER.debug('encoding lua tables')

        LOGGER.debug('encoding map resource')
        with open(self.map_res_file, mode='w', encoding=ENCODING) as f:
            f.write(SLTP().encode(self._map_res, self._map_res_qual))

        LOGGER.debug('encoding l10n dictionary')
        with open(self.dictionary_file, mode='w', encoding=ENCODING) as f:
            f.write(SLTP().encode(self.l10n, self._l10n_qual))
        LOGGER.debug('encoding mission dictionary')
        with open(self.mission_file, mode='w', encoding=ENCODING) as f:
            f.write(SLTP().encode(self.mission.d, self._mission_qual))

        LOGGER.debug('encoding done')

    def _check_extracted_content(self):

        for filename in self.zip_content:
            p = self.tmpdir.joinpath(filename)
            if not p.exists():
                raise FileNotFoundError(p.absolute())

    def _extract_files_from_zip(self, zip_file):

        for item in zip_file.infolist():  # not using ZipFile.extractall() for security reasons
            assert isinstance(item, ZipInfo)

            LOGGER.debug('unzipping item: {}'.format(item.filename))

            try:
                zip_file.extract(item, self.tmpdir.absolute())
            except:
                LOGGER.error('failed to extract archive member: {}'.format(item.filename))
                raise

    def _remove_temp_dir(self):
        shutil.rmtree(self.tmpdir.absolute())

    def unzip(self, overwrite: bool = False):

        if self.zip_content and not overwrite:
            raise FileExistsError(self.tmpdir.absolute())

        LOGGER.debug('unzipping miz to temp dir')

        try:

            path = str(self.miz_path.absolute())
            with ZipFile(path) as zip_file:

                LOGGER.debug('reading infolist')

                self.zip_content = [f.filename for f in zip_file.infolist()]

                self._extract_files_from_zip(zip_file)

        except BadZipFile:
            raise BadZipFile(self.miz_path.absolute())

        except:
            LOGGER.exception('error while unzipping miz file: {}'.format(self.miz_path.absolute()))
            raise

        LOGGER.debug('checking miz content')

        # noinspection PyTypeChecker
        for miz_item in map(
            join,
            [self.tmpdir.absolute()],
            [
                'mission',
                'options',
                'warehouses',
                'l10n/DEFAULT/dictionary',
                'l10n/DEFAULT/mapResource'
            ]
        ):

            if not exists(miz_item):
                LOGGER.error('missing file in miz: {}'.format(miz_item))
                raise FileNotFoundError(miz_item)

        self._check_extracted_content()

        LOGGER.debug('all files have been found, miz successfully unzipped')

    def zip(self, destination=None):

        self._encode()

        if destination is None:
            destination = Path(self.miz_path.parent).joinpath('{}_EMFT.miz'.format(self.miz_path.name))

        destination = Path(destination).absolute()

        LOGGER.debug('zipping mission to: {}'.format(destination))

        with open(destination, mode='wb') as f:
            f.write(dummy_miz)

        with ZipFile(destination, mode='w', compression=8) as _z:

            for f in self.zip_content:
                abs_path = self.tmpdir.joinpath(f).absolute()
                LOGGER.debug('injecting in zip file: {}'.format(abs_path))
                _z.write(abs_path, arcname=f)

        return destination
