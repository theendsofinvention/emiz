# coding=utf-8
"""
Add JSON composition to Miz object
"""
import shutil
import typing
import ujson
from pathlib import Path

import elib
import pathvalidate
from natsort import natsorted

from emiz.miz import ENCODING, Miz
from emiz.sltp import SLTP

NAME_FIELDS = ['callsignStr', 'name']

LOGGER = elib.custom_logging.get_logger('EMIZ')


def wrong_version(obj_name, obj_version, expected_version):
    """
    Triggers when version differs

    Args:
        obj_name: json object name
        obj_version: json object version
        expected_version: expected version
    """
    print(f'WARNING: {obj_name} version is {obj_version}; expected version: {expected_version}')


class NewMiz(Miz):
    """
    Add JSON composition to Miz object
    """
    missing_name_counter = 0
    version = 0

    def __init__(
            self,
            path_to_miz_file: typing.Union[str, Path],
            temp_dir: typing.Union[str, Path] = None,
            keep_temp_dir: bool = False,
            overwrite: bool = False
    ) -> None:
        Miz.__init__(self, path_to_miz_file, temp_dir, keep_temp_dir, overwrite)

    @staticmethod
    def _missing_name():
        NewMiz.missing_name_counter += 1
        return f'__MISSING_NAME #{NewMiz.missing_name_counter:03d}'

    @staticmethod
    def _check_resource(resource_name, miz: Miz):
        if resource_name not in miz.resources:
            raise FileNotFoundError(f'resource not found: {resource_name}')

    @staticmethod
    def _translate(dict_key, miz: Miz):
        if isinstance(dict_key, str):
            if dict_key.startswith('DictKey_'):
                try:
                    return miz.l10n[dict_key]
                except KeyError:
                    miz.l10n[dict_key] = NewMiz._missing_name()
                    return miz.l10n[dict_key]
            elif dict_key.startswith('ResKey_'):
                try:
                    resource_name = miz.map_res[dict_key]
                except KeyError:
                    miz.map_res[dict_key] = NewMiz._missing_name()
                    resource_name = NewMiz._missing_name()
                NewMiz._check_resource(resource_name, miz)
                return resource_name
        return dict_key

    @staticmethod
    def _write_output_to_file(file: Path, output: dict):
        # pylint: disable=c-extension-no-member
        file.write_text(ujson.dumps(output, indent=2, ensure_ascii=False), encoding=ENCODING)

    @staticmethod
    def _decompose_list_dict(dict_: dict, output_folder: Path, version, miz: Miz):
        count = 1
        order: typing.Dict[str, int] = {}
        for key in dict_:
            sub_dict = dict_[key]
            name = None
            for name_field in NAME_FIELDS:
                try:
                    name = sub_dict[name_field]
                except KeyError:
                    pass
            if name is None:
                raise ValueError('Name not found')
            name = NewMiz._translate(name, miz)
            if not name:
                name = str(NewMiz._translate(key, miz))
            name = pathvalidate.sanitize_filename(name)
            sub_count = 1
            while name in order:
                name = f'{name} #{sub_count:03d}'
            order[name] = count
            count += 1
            subfolder = Path(output_folder, name)
            NewMiz._decompose_dict(sub_dict, f'__{NewMiz._translate(name, miz)}', subfolder, version, miz)
        order = {k: order[k] for k in natsorted(order.keys())}
        NewMiz._write_output_to_file(Path(output_folder, '__order__.json'), order)

    @staticmethod
    def _decompose_dict(dict_: dict, key_name: str, output_folder: Path, version, miz: Miz):
        output = {}
        output_folder.mkdir(exist_ok=True)
        try:
            first_key = next(iter(dict_))
            first_value = dict_[first_key]
        except (StopIteration, TypeError):
            first_key = None
            first_value = None
        if first_key and dict_ and isinstance(first_key, int) and isinstance(first_value, dict):
            if [name_field for name_field in NAME_FIELDS if name_field in first_value]:
                NewMiz._decompose_list_dict(dict_, output_folder, version, miz)
                return

        is_single = True
        for key in dict_:
            value = dict_[key]
            if not key == 'properties' and isinstance(value, dict) and value:
                is_single = False
                subfolder_name = pathvalidate.sanitize_filename(str(NewMiz._translate(key, miz)))
                subfolder = Path(output_folder, subfolder_name)
                NewMiz._decompose_dict(value, f'__{key}', subfolder, version, miz)
            else:
                # output[key] = NewMiz._translate(dict_[key], miz)
                output[key] = dict_[key]
        if output:
            output['__version__'] = version
            key_name = pathvalidate.sanitize_filename(str(key_name))
            if not is_single:
                file = Path(output_folder, f'{key_name}.json')
            else:
                output_folder.rmdir()
                file = Path(f'{output_folder}.json')
            NewMiz._write_output_to_file(file, output)

    @staticmethod
    def _sorted(dict_: dict) -> dict:
        for k in dict_:
            try:
                int_key = int(k)
            except ValueError:
                pass
            else:
                value = dict_[k]
                del dict_[k]
                dict_[int_key] = value
        return {k: dict_[k] for k in natsorted(dict_.keys())}

    @staticmethod
    def _recreate_dict_from_folder(folder: Path, version) -> dict:
        output = {}
        folder_stem = folder.name.replace('.json', '')
        if Path(folder, '__order__.json').exists():
            output.update(NewMiz._recreate_dict_from_ordered_folder(folder, version))
        else:
            for obj in folder.iterdir():
                obj_stem: typing.Union[str, int] = obj.name.replace('.json', '')
                try:
                    obj_stem = int(obj_stem)
                except ValueError:
                    pass
                if obj.is_file():
                    if obj_stem == 'base_info':
                        output.update(NewMiz._recreate_dict_from_file(obj.absolute(), version))
                    else:
                        if obj_stem == f'__{folder_stem}':
                            output.update(NewMiz._recreate_dict_from_file(obj.absolute(), version)[obj_stem])
                        else:
                            value = NewMiz._recreate_dict_from_file(obj.absolute(), version)
                            output[obj_stem] = value[obj_stem]
                elif obj.is_dir():
                    output[obj_stem] = NewMiz._recreate_dict_from_folder(obj.absolute(), version)
        return NewMiz._sorted(output)

    @staticmethod
    def _recreate_dict_from_ordered_folder(folder: Path, version) -> dict:
        output = {}
        order_file = Path(folder, '__order__.json')
        # pylint: disable=c-extension-no-member
        order = ujson.loads(order_file.read_text(encoding=ENCODING))
        for obj in folder.iterdir():
            obj_stem: typing.Union[str, int] = obj.name.replace('.json', '')
            try:
                obj_stem = int(obj_stem)
            except ValueError:
                pass
            if obj.is_file():
                if obj_stem == '__order__':
                    continue
                index = order[obj.name.replace('.json', '')]
                output[int(index)] = NewMiz._recreate_dict_from_file(obj.absolute(), version)[obj_stem]

            elif obj.is_dir():
                index = order[obj.name.replace('.json', '')]
                output[int(index)] = NewMiz._recreate_dict_from_folder(obj.absolute(), version)
        return NewMiz._sorted(output)

    @staticmethod
    def _recreate_dict_from_file(file: Path, version) -> dict:
        output = {}
        content = file.read_text(encoding=ENCODING)
        # pylint: disable=c-extension-no-member
        dict_ = ujson.loads(content, precise_float=True)

        dict_version = dict_.pop('__version__')
        if dict_version != version:
            wrong_version(file.absolute(), dict_version, version)

        file_stem: typing.Union[str, int] = file.name.replace('.json', '')
        try:
            file_stem = int(file_stem)
        except ValueError:
            pass
        if file_stem == 'base_info':
            return NewMiz._sorted(dict_)

        output[file_stem] = NewMiz._sorted(dict_)

        for key in dict_:
            if isinstance(key, str) and key.startswith('__'):
                raise ValueError(f'Unprocessed key: {key}')
        return NewMiz._sorted(output)

    @staticmethod
    def _get_subfolders(output_folder: Path):
        mission_folder = output_folder.joinpath('mission').absolute()
        assets_folder = output_folder.joinpath('assets').absolute()
        return mission_folder, assets_folder

    @staticmethod
    def _wipe_folders(*folders: Path):
        for folder in folders:
            folder = Path(folder).absolute()
            if folder.exists():
                LOGGER.info('removing: %s', folder)
                shutil.rmtree(folder)

    @staticmethod
    def _reorder_warehouses(assets_folder):
        path = Path(assets_folder, 'warehouses')
        if path.exists():
            parser = SLTP()
            data, qual = parser.decode(path.read_text(encoding=ENCODING))
            path.write_text(parser.encode(data, qual), encoding=ENCODING)

    @staticmethod
    def decompose(miz_file: Path, output_folder: Path):
        """
        Decompose this Miz into json

        Args:
            output_folder: folder to output the json structure as a Path
            miz_file: MIZ file path as a Path
        """
        mission_folder, assets_folder = NewMiz._get_subfolders(output_folder)
        NewMiz._wipe_folders(mission_folder, assets_folder)
        LOGGER.info('unzipping mission file')
        with Miz(miz_file) as miz:
            version = miz.mission.d['version']
            LOGGER.debug(f'mission version: "%s"', version)

            LOGGER.info('copying assets to: "%s"', assets_folder)
            ignore = shutil.ignore_patterns('mission')
            shutil.copytree(str(miz.temp_dir), str(assets_folder), ignore=ignore)

            NewMiz._reorder_warehouses(assets_folder)

            LOGGER.info('decomposing mission table into: "%s" (this will take a while)', mission_folder)
            NewMiz._decompose_dict(miz.mission.d, 'base_info', mission_folder, version, miz)

    @staticmethod
    def recompose(src: Path, target_file: Path):
        """
        Recompose a Miz from json object

        Args:
            src: folder containing the json structure
            target_file: target Miz file
        """
        mission_folder, assets_folder = NewMiz._get_subfolders(src)
        # pylint: disable=c-extension-no-member
        base_info = ujson.loads(Path(mission_folder, 'base_info.json').read_text(encoding=ENCODING))
        version = base_info['__version__']
        with Miz(target_file) as miz:
            LOGGER.info('re-composing mission table from folder: "%s"', mission_folder)
            miz.mission.d = NewMiz._recreate_dict_from_folder(mission_folder, version)
            for item in assets_folder.iterdir():
                target = Path(miz.temp_dir, item.name).absolute()
                if item.is_dir():
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(item.absolute(), target)
                elif item.is_file():
                    shutil.copy(item.absolute(), target)
            miz.zip(target_file, encode=False)

        # dict_ = self.
        # pylint: disable=c-extension-no-member
        # self.mi
        # self._encode()
        # self.zip(target_file)
