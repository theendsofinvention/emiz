# coding=utf-8
"""
Manages MIZ files
"""
import shutil
import tempfile
import typing
from filecmp import dircmp
from pathlib import Path
from zipfile import BadZipFile, ZipFile, ZipInfo

import elib.path

from emiz import MAIN_LOGGER
from emiz.dummy_miz import dummy_miz
from emiz.mission import Mission
from emiz.sltp import SLTP

LOGGER = MAIN_LOGGER.getChild(__name__)
ENCODING = 'iso8859_15'


# pylint: disable=too-many-instance-attributes
class Miz:
    """
    Manage MIZ files
    """

    def __init__(
            self,
            path_to_miz_file: typing.Union[str, Path],
            temp_dir: typing.Union[str, Path] = None,
            keep_temp_dir: bool = False,
            overwrite: bool = False
    ):

        self.miz_path = elib.path.ensure_file(path_to_miz_file)

        if self.miz_path.suffix != '.miz':
            raise ValueError(f'MIZ file should end with the ".miz" extension: {self.miz_path}')

        if temp_dir is not None:
            raise PendingDeprecationWarning()

        self.keep_temp_dir = keep_temp_dir

        self.overwrite = overwrite

        self.temp_dir = Path(tempfile.mkdtemp('EMFT_'))
        LOGGER.debug(f'temporary directory: {self.temp_dir}')

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
        self.decode()
        return self

    def __exit__(self, exc_type, exc_val, _):
        if exc_type:
            LOGGER.error(f'there were error with this mission, keeping temp dir at "{self.temp_dir}"')
            LOGGER.error('{}\n{}'.format(exc_type, exc_val))
            return False

        LOGGER.debug('closing Mission object context')
        if not self.keep_temp_dir:
            LOGGER.debug(f'removing temp dir: {self.temp_dir}')
            self._remove_temp_dir()
        return True

    @property
    def mission_file(self) -> Path:
        """

        Returns: mission file path

        """
        return self.temp_dir.joinpath('mission')

    @property
    def dictionary_file(self) -> Path:
        """

        Returns: l10n file path

        """
        return self.temp_dir.joinpath('l10n', 'DEFAULT', 'dictionary')

    @property
    def map_res_file(self) -> Path:
        """

        Returns: resource map file path

        """
        return self.temp_dir.joinpath('l10n', 'DEFAULT', 'mapResource')

    @property
    def mission(self) -> Mission:
        """

        Returns: mission

        """
        if self._mission is None:
            raise RuntimeError()
        return self._mission

    @property
    def l10n(self) -> dict:
        """

        Returns: l10n dictionary

        """
        if self._l10n is None:
            raise RuntimeError()
        return self._l10n

    @property
    def map_res(self) -> dict:
        """

        Returns: map resources dictionary

        """
        if self._map_res is None:
            raise RuntimeError()
        return self._map_res

    @staticmethod
    def reorder(
            miz_file_path: typing.Union[str, Path],
            target_dir: typing.Union[str, Path],
            skip_options_file: bool,
    ):
        """
        Re-orders a miz file into a folder (flattened)

        Args:
            miz_file_path: source miz file
            target_dir: folder to flatten the content into
            skip_options_file: do not re-order option file

        """

        miz_file_path = elib.path.ensure_file(miz_file_path)
        target_dir = elib.path.ensure_dir(target_dir, must_exist=False)

        LOGGER.debug(f're-ordering miz file: {miz_file_path}')
        LOGGER.debug(f'destination folder: {target_dir}')
        LOGGER.debug(f'{"skipping" if skip_options_file else "including"} option file')

        if not target_dir.exists():
            LOGGER.debug(f'creating directory {target_dir}')
            target_dir.mkdir(exist_ok=True)

        with Miz(miz_file_path, overwrite=True) as miz_:

            def mirror_dir(src: Path, dst: Path):
                """
                Propagates difference between the original lua tables and the re-ordered one

                Args:
                    src: source folder
                    dst: destination folder
                """
                LOGGER.debug(f'mirroring: {src} -> {dst}')

                LOGGER.debug('comparing directories')
                diff_ = dircmp(str(src), str(dst), ignore)

                diff_list = diff_.left_only + diff_.diff_files
                LOGGER.debug(f'differences: {diff_list}')

                for __diff in diff_list:
                    source = Path(diff_.left, __diff)
                    target = Path(diff_.right, __diff)
                    LOGGER.debug(f'looking at: {__diff}')
                    if source.is_dir():
                        LOGGER.debug('isdir: {}'.format(__diff))
                        if not target.exists():
                            LOGGER.debug(f'creating: {__diff}')
                            target.mkdir()
                        mirror_dir(source, target)
                    else:
                        LOGGER.debug(f'copying: {__diff}')
                        shutil.copy2(str(source), diff_.right)
                for sub in diff_.subdirs.values():
                    assert isinstance(sub, dircmp)
                    mirror_dir(sub.left, sub.right)

            # pylint: disable=protected-access
            miz_._encode()

            if skip_options_file:
                ignore = ['options']
            else:
                ignore = []

            mirror_dir(miz_.temp_dir, target_dir)

    def decode(self):
        """Decodes the mission files into dictionaries"""

        LOGGER.debug('decoding lua tables')

        if not self.zip_content:
            self.unzip(overwrite=False)

        LOGGER.debug('reading map resource file')
        with open(self.map_res_file, encoding=ENCODING) as stream:
            self._map_res, self._map_res_qual = SLTP().decode(stream.read())

        LOGGER.debug('reading l10n file')
        with open(self.dictionary_file, encoding=ENCODING) as stream:
            self._l10n, self._l10n_qual = SLTP().decode(stream.read())

        LOGGER.debug('reading mission file')
        with open(self.mission_file, encoding=ENCODING) as stream:
            mission_data, self._mission_qual = SLTP().decode(stream.read())
            self._mission = Mission(mission_data, self._l10n)

        LOGGER.debug('decoding done')

    def _encode(self):

        LOGGER.debug('encoding lua tables')

        LOGGER.debug('encoding map resource')
        with open(self.map_res_file, mode='w', encoding=ENCODING) as stream:
            stream.write(SLTP().encode(self._map_res, self._map_res_qual))

        LOGGER.debug('encoding l10n dictionary')
        with open(self.dictionary_file, mode='w', encoding=ENCODING) as stream:
            stream.write(SLTP().encode(self.l10n, self._l10n_qual))

        LOGGER.debug('encoding mission dictionary')
        with open(self.mission_file, mode='w', encoding=ENCODING) as stream:
            stream.write(SLTP().encode(self.mission.d, self._mission_qual))

        LOGGER.debug('encoding done')

    def _check_extracted_content(self):

        for filename in self.zip_content:
            path = Path(self.temp_dir.joinpath(filename))
            if not path.exists():
                raise FileNotFoundError(str(path))

    def _extract_files_from_zip(self, zip_file):

        for item in zip_file.infolist():  # not using ZipFile.extractall() for security reasons
            assert isinstance(item, ZipInfo)

            LOGGER.debug(f'unzipping item: {item.filename}')

            try:
                zip_file.extract(item, str(self.temp_dir))
            except:  # noqa: E722
                LOGGER.error(f'failed to extract archive member: {item.filename}')
                raise

    def _remove_temp_dir(self):
        shutil.rmtree(str(self.temp_dir))

    def unzip(self, overwrite: bool = False):
        """
        Flattens a MIZ file into the temp dir

        Args:
            overwrite: allow overwriting exiting files

        """

        if self.zip_content and not overwrite:
            raise FileExistsError(str(self.temp_dir))

        LOGGER.debug('unzipping miz to temp dir')

        try:

            with ZipFile(str(self.miz_path)) as zip_file:

                LOGGER.debug('reading infolist')

                self.zip_content = [f.filename for f in zip_file.infolist()]

                self._extract_files_from_zip(zip_file)

        except BadZipFile:
            raise BadZipFile(str(self.miz_path))

        except:  # noqa: E722
            LOGGER.exception(f'error while unzipping miz file: {self.miz_path}')
            raise

        LOGGER.debug('checking miz content')

        # noinspection PyTypeChecker
        for miz_item in ['mission', 'options', 'warehouses', 'l10n/DEFAULT/dictionary', 'l10n/DEFAULT/mapResource']:
            if not Path(self.temp_dir.joinpath(miz_item)).exists():
                LOGGER.error('missing file in miz: {}'.format(miz_item))
                raise FileNotFoundError(miz_item)

        self._check_extracted_content()

        LOGGER.debug('all files have been found, miz successfully unzipped')

    def zip(self, destination: typing.Union[str, Path] = None) -> str:
        """
        Write mission, dictionary etc. to a MIZ file

        Args:
            destination: target MIZ file (if none, defaults to source MIZ + "_EMIZ"

        Returns: destination file

        """

        self._encode()

        if destination is None:
            destination = self.miz_path.parent.joinpath(f'{self.miz_path.stem}_EMIZ.miz')
        else:
            destination = elib.path.ensure_file(destination, must_exist=False)

        LOGGER.debug('zipping mission to: {}'.format(destination))

        destination.write_bytes(dummy_miz)

        with ZipFile(str(destination), mode='w', compression=8) as zip_file:

            for zip_content in self.zip_content:
                file = Path(self.temp_dir.joinpath(zip_content))
                LOGGER.debug(f'injecting in zip file: {file}')
                zip_file.write(str(file), arcname=zip_content)

        return str(destination)
