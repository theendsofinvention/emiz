# coding=utf-8
import ujson
from pathlib import Path

import pathvalidate
from natsort import natsorted

from emiz.miz import ENCODING, Miz


class Decomposer2:

    name_fields = ['callsignStr', 'name']

    def __init__(self, miz: Miz):
        self._dict = miz.mission.d
        self._l10n = miz.l10n
        self._map = miz.map_res
        self._version = self._dict['version']
        self._missing_name_counter = 0

    def _missing_name(self):
        self._missing_name_counter += 1
        return f'__MISSING_NAME #{self._missing_name_counter:03d}'

    def _translate(self, dict_key):
        if isinstance(dict_key, str) \
                and dict_key.startswith('DictKey_'):
            try:
                return self._l10n[dict_key]
            except KeyError:
                self._l10n[dict_key] = self._missing_name()
                return self._l10n[dict_key]
                # TODO: l10n is missing a name !!!
                pass
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

    def decompose(self, output_folder: Path):
        self._decompose_dict(self._dict, 'base_info', output_folder)



if __name__ == '__main__':
    import shutil
    test_file = './test/test_files/TRMT_6.4.3.miz'
    # test_file = './test/test_files/TRG_KA50.miz'
    test_folder = 'test_decompose'

    # for x in test_folder.absolute().rglob('*'):
    #     if Path(x).is_dir():
    #         print(x)

    if Path(test_folder).exists():
        shutil.rmtree(test_folder)
    test_folder = Path(test_folder)
    with Miz(test_file) as miz_:
        # print(miz_.mission.d['weather'])
        # decomposer = Decomposer(miz_, output_folder)
        Path('test_decompose.json').write_text(ujson.dumps(miz_.mission.d, indent=4, ensure_ascii=False), encoding=ENCODING)
        Decomposer2(miz_).decompose(test_folder)

# TODO: isolate triggers & trigrules (name value is "comment" on trigrules
