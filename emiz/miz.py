# coding=utf-8
"""
Manages MIZ files
"""
import os
import shutil
import tempfile
from filecmp import dircmp
from zipfile import BadZipFile, ZipFile, ZipInfo

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

    def __init__(self, path_to_miz_file, temp_dir=None, keep_temp_dir: bool = False, overwrite: bool = False):

        self.miz_path = os.path.abspath(path_to_miz_file)

        if not os.path.exists(self.miz_path):
            raise FileNotFoundError(path_to_miz_file)

        if not os.path.isfile(self.miz_path):
            raise TypeError(path_to_miz_file)

        if not os.path.splitext(self.miz_path)[1] == '.miz':
            raise ValueError(path_to_miz_file)

        if temp_dir is not None:
            raise PendingDeprecationWarning()

        self.keep_temp_dir = keep_temp_dir

        self.overwrite = overwrite

        self.temp_dir = tempfile.mkdtemp('EMFT_')
        LOGGER.debug('temporary directory: {}'.format(os.path.abspath(self.temp_dir)))

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
                os.path.abspath(self.temp_dir)))
            LOGGER.error('{}\n{}'.format(exc_type, exc_val))
            return False

        LOGGER.debug('closing Mission object context')
        if not self.keep_temp_dir:
            LOGGER.debug('removing temp dir: {}'.format(os.path.abspath(self.temp_dir)))
            self._remove_temp_dir()
        return True

    @property
    def mission_file(self):
        """

        Returns: mission file path

        """
        return os.path.join(self.temp_dir, 'mission')

    @property
    def dictionary_file(self):
        """

        Returns: l10n file path

        """
        return os.path.join(self.temp_dir, 'l10n', 'DEFAULT', 'dictionary')

    @property
    def map_res_file(self):
        """

        Returns: resource map file path

        """
        return os.path.join(self.temp_dir, 'l10n', 'DEFAULT', 'mapResource')

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
    def reorder(miz_file_path, target_dir, skip_options_file):
        """
        Re-orders a miz file into a folder (flattened)

        Args:
            miz_file_path: source miz file
            target_dir: folder to flatten the content into
            skip_options_file: do not re-order option file

        """

        LOGGER.debug('re-ordering miz file: {}'.format(miz_file_path))
        LOGGER.debug('destination folder: {}'.format(target_dir))
        LOGGER.debug('{}option file'.format('skipping' if skip_options_file else 'including'))

        if not os.path.exists(target_dir):
            LOGGER.debug(f'creating directory {target_dir}')
            os.makedirs(target_dir)

        with Miz(miz_file_path, overwrite=True) as miz_:

            def mirror_dir(src, dst):
                """
                Propagates difference between the original lua tables and the re-ordered one

                Args:
                    src: source folder
                    dst: destination folder
                """
                LOGGER.debug('{} -> {}'.format(src, dst))
                diff_ = dircmp(src, dst, ignore)
                diff_list = diff_.left_only + diff_.diff_files
                LOGGER.debug('differences: {}'.format(diff_list))
                for __diff in diff_list:
                    source = os.path.abspath(os.path.join(diff_.left, __diff))
                    target = os.path.abspath(os.path.join(diff_.right, __diff))
                    LOGGER.debug('looking at: {}'.format(__diff))
                    if os.path.isdir(source):
                        LOGGER.debug('isdir: {}'.format(__diff))
                        if not os.path.exists(target):
                            LOGGER.debug('creating: {}'.format(__diff))
                            os.mkdir(target)
                        mirror_dir(source, target)
                    else:
                        LOGGER.debug('copying: {}'.format(__diff))
                        shutil.copy2(source, diff_.right)
                for sub in diff_.subdirs.values():
                    assert isinstance(sub, dircmp)
                    mirror_dir(sub.left, sub.right)

            miz_._encode()  # pylint: disable=protected-access

            if skip_options_file:
                ignore = ['options']
            else:
                ignore = []

            mirror_dir(miz_.temp_dir, target_dir)

    def _decode(self):

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
            path = os.path.abspath(os.path.join(self.temp_dir, filename))
            if not os.path.exists(path):
                raise FileNotFoundError(path)

    def _extract_files_from_zip(self, zip_file):

        for item in zip_file.infolist():  # not using ZipFile.extractall() for security reasons
            assert isinstance(item, ZipInfo)

            LOGGER.debug('unzipping item: {}'.format(item.filename))

            try:
                zip_file.extract(item, os.path.abspath(self.temp_dir))
            except:  # noqa: E722
                LOGGER.error('failed to extract archive member: {}'.format(item.filename))
                raise

    def _remove_temp_dir(self):
        shutil.rmtree(os.path.abspath(self.temp_dir))

    def unzip(self, overwrite: bool = False):
        """
        Flattens a MIZ file into the temp dir

        Args:
            overwrite: allow overwriting exiting files

        """

        if self.zip_content and not overwrite:
            raise FileExistsError(os.path.abspath(self.temp_dir))

        LOGGER.debug('unzipping miz to temp dir')

        try:

            with ZipFile(self.miz_path) as zip_file:

                LOGGER.debug('reading infolist')

                self.zip_content = [f.filename for f in zip_file.infolist()]

                self._extract_files_from_zip(zip_file)

        except BadZipFile:
            raise BadZipFile(self.miz_path)

        except:  # noqa: E722
            LOGGER.exception('error while unzipping miz file: {}'.format(self.miz_path))
            raise

        LOGGER.debug('checking miz content')

        # noinspection PyTypeChecker
        for miz_item in map(
                os.path.join,
                [os.path.abspath(self.temp_dir)],
                [
                    'mission',
                    'options',
                    'warehouses',
                    'l10n/DEFAULT/dictionary',
                    'l10n/DEFAULT/mapResource'
                ]
        ):

            if not os.path.exists(miz_item):
                LOGGER.error('missing file in miz: {}'.format(miz_item))
                raise FileNotFoundError(miz_item)

        self._check_extracted_content()

        LOGGER.debug('all files have been found, miz successfully unzipped')

    def zip(self, destination=None) -> str:
        """
        Write mission, dictionary etc. to a MIZ file

        Args:
            destination: target MIZ file (if none, defaults to source MIZ + "_EMIZ"

        Returns: destination file

        """

        self._encode()

        if destination is None:
            destination = os.path.join(
                os.path.dirname(self.miz_path),
                '{}_EMIZ.miz'.format(os.path.basename(self.miz_path))
            )

        destination = os.path.abspath(destination)

        LOGGER.debug('zipping mission to: {}'.format(destination))

        with open(destination, mode='wb') as stream:
            stream.write(dummy_miz)

        with ZipFile(destination, mode='w', compression=8) as zip_file:

            for zip_content in self.zip_content:
                abs_path = os.path.abspath(os.path.join(self.temp_dir, zip_content))
                LOGGER.debug('injecting in zip file: {}'.format(abs_path))
                zip_file.write(abs_path, arcname=zip_content)

        return destination
