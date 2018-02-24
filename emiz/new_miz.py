# coding=utf-8
import typing
import ujson
from pathlib import Path

import pathvalidate
from natsort import natsorted

from emiz.miz import Miz, ENCODING


def wrong_version(obj_name, obj_version, expected_version):
    print(f'WARNING: {obj_name} version is {obj_version}; expected version: {expected_version}')


class NewMiz(Miz):


    name_fields = ['callsignStr', 'name']

    def __init__(
            self,
            path_to_miz_file: typing.Union[str, Path],
            temp_dir: typing.Union[str, Path] = None,
            keep_temp_dir: bool = False,
            overwrite: bool = False
    ):
        Miz.__init__(self, path_to_miz_file, temp_dir, keep_temp_dir, overwrite)
        self._version = 0
        self._missing_name_counter = 0

    def _missing_name(self):
        self._missing_name_counter += 1
        return f'__MISSING_NAME #{self._missing_name_counter:03d}'

    def _check_resource(self, resource_name):
        if resource_name not in self._resources:
            raise FileNotFoundError(f'resource not found: {resource_name}')

    def _translate(self, dict_key):
        if isinstance(dict_key, str):
            if dict_key.startswith('DictKey_'):
                try:
                    return self._l10n[dict_key]
                except KeyError:
                    self._l10n[dict_key] = self._missing_name()
                    return self._l10n[dict_key]
            elif dict_key.startswith('ResKey_'):
                try:
                    resource_name = self.map_res[dict_key]
                except KeyError:
                    resource_name = self._missing_name()
                self._check_resource(resource_name)
                return resource_name
        return dict_key

    def _write_output_to_file(self, file: Path, output: dict):
        file.write_text(ujson.dumps(output, indent=2, ensure_ascii=False), encoding=ENCODING)

    def _decompose_list_dict(self, dict_: dict, output_folder: Path):
        count = 1
        order = {}
        for key in dict_:
            sub_dict = dict_[key]
            name = None
            for name_field in self.name_fields:
                try:
                    name = sub_dict[name_field]
                except KeyError:
                    pass
            if name is None:
                raise ValueError('Name not found')
            name = self._translate(name)
            if not name:
                name = str(key)
            name = pathvalidate.sanitize_filename(name)
            sub_count = 1
            while name in order:
                name = f'{name} #{sub_count:03d}'
            order[name] = count
            count += 1
            subfolder = Path(output_folder, name)
            self._decompose_dict(sub_dict, f'__{name}', subfolder)
        order = {k: order[k] for k in natsorted(order.keys())}
        self._write_output_to_file(Path(output_folder, '__order__.json'), order)

    def _decompose_dict(self, dict_: dict, key_name: str, output_folder: Path):
        output = {}
        output_folder.mkdir(exist_ok=True)
        try:
            first_key = next(iter(dict_))
            first_value = dict_[first_key]
        except (StopIteration, TypeError):
            first_key = None
            first_value = None
        if first_key and dict_ and isinstance(first_key, int) and isinstance(first_value, dict):
            if [name_field for name_field in self.name_fields if name_field in first_value]:
                self._decompose_list_dict(dict_, output_folder)
                return

        is_single = True
        for key in dict_:
            value = dict_[key]
            if not key == 'properties' and isinstance(value, dict) and value:
                is_single = False
                subfolder_name = pathvalidate.sanitize_filename(str(key))
                subfolder = Path(output_folder, subfolder_name)
                self._decompose_dict(value, f'__{key}', subfolder)
            else:
                output[key] = self._translate(dict_[key])
        if output:
            output['__version__'] = self._version
            key_name = pathvalidate.sanitize_filename(str(key_name))
            if not is_single:
                file = Path(output_folder, f'{key_name}.json')
            else:
                output_folder.rmdir()
                file = Path(f'{output_folder}.json')
            self._write_output_to_file(file, output)

    @staticmethod
    def _sorted(dict_: dict) -> dict:
        return {k: dict_[k] for k in natsorted(dict_.keys())}

    def _recreate_dict_from_folder(self, folder: Path) -> dict:
        output = {}
        folder_stem = folder.name.replace('.json', '')
        if Path(folder, '__order__.json').exists():
            output.update(self._recreate_dict_from_ordered_folder(folder))
        else:
            for obj in folder.iterdir():
                obj_stem = obj.name.replace('.json', '')
                if obj.is_file():
                    if obj_stem == 'base_info':
                        output.update(self._recreate_dict_from_file(obj.absolute()))
                    else:
                        if obj_stem == f'__{folder_stem}':
                            output.update(self._recreate_dict_from_file(obj.absolute())[obj_stem])
                        else:
                            output[obj_stem] = self._recreate_dict_from_file(obj.absolute())[obj_stem]
                elif obj.is_dir():
                    output[obj_stem] = self._recreate_dict_from_folder(obj.absolute())
        return self._sorted(output)

    def _recreate_dict_from_ordered_folder(self, folder: Path) -> dict:
        output = {}
        order_file = Path(folder, '__order__.json')
        order = ujson.loads(order_file.read_text(encoding=ENCODING))
        # order = {v: k for k, v in order.items()}
        # order_file.unlink()
        for obj in folder.iterdir():
            obj_stem = obj.name.replace('.json', '')
            if obj.is_file():
                if obj_stem == '__order__':
                    continue
                index = order[obj.name.replace('.json', '')]
                output[f'{index}'] = self._recreate_dict_from_file(obj.absolute())[obj_stem]

            elif obj.is_dir():
                index = order[obj.name.replace('.json', '')]
                output[f'{index}'] = self._recreate_dict_from_folder(obj.absolute())
        return self._sorted(output)

    def _recreate_dict_from_file(self, file: Path) -> dict:
        output = {}
        content = file.read_text(encoding=ENCODING)
        dict_ = ujson.loads(content, precise_float=True)
        # with file.open('rb') as stream:
        #     dict_ = ujson.load(stream, precise_float=True)
        assert isinstance(dict_, dict)

        dict_version = dict_.pop('__version__')
        if dict_version != self._version:
            wrong_version(file.absolute(), dict_version, self._version)

        file_stem = file.name.replace('.json', '')
        if file_stem == 'base_info':
            return self._sorted(dict_)
        else:
            output[file_stem] = self._sorted(dict_)

        for key in dict_:
            if isinstance(key, str) and key.startswith('__'):
                raise ValueError(f'Unprocessed key: {key}')
        return self._sorted(output)

    def decompose(self, output_folder: Path):
        self.unzip()
        self.decode()
        self._version = self.mission.d['version']
        self._decompose_dict(self.mission.d, 'base_info', output_folder)

    def recompose(self, src: Path, target_file: Path):
        dict_ = self._recreate_dict_from_folder(src)
        Path('test_recompose.json').write_text(ujson.dumps(dict_, indent=4, ensure_ascii=False), encoding=ENCODING)
        self._encode()
        self.zip(target_file)


if __name__ == '__main__':

    import elib
    import shutil

    test_file = './test/test_files/TRMT_6.4.3.miz'
    logger = elib.custom_logging.get_logger('EMIZ')
    elib.custom_logging.set_handler_level('EMIZ', 'ch', 'debug')
    elib.custom_logging.set_root_logger(logger)
    test_folder = Path('test_decompose').absolute()
    if test_folder.exists():
        shutil.rmtree(test_folder)
    miz = NewMiz(test_file)
    miz.decompose(test_folder)
    miz.recompose(test_folder, Path('test.miz'))
