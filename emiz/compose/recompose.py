# coding=utf-8

import ujson
from pathlib import Path
from natsort import natsorted



from emiz.miz import ENCODING


def wrong_version(obj_name, obj_version, expected_version):
    print(f'WARNING: {obj_name} version is {obj_version}; expected version: {expected_version}')


class Recompose:
    def __init__(self, src: Path):
        self._src = src.absolute()
        self._dict = {}
        content = Path(src, 'base_info.json').read_text(encoding=ENCODING)
        self._version = ujson.loads(content)['version']

    def recompose(self):
        self._dict = self._recreate_dict_from_folder(self._src)
        Path('test_recompose.json').write_text(ujson.dumps(self._dict, indent=4, ensure_ascii=False), encoding=ENCODING)

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


if __name__ == '__main__':
    test_folder = Path('test_decompose')
    recomposer = Recompose(test_folder)
    recomposer.recompose()
