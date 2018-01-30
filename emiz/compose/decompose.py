# coding=utf-8
import copy
import typing
import ujson
from pathlib import Path
import pathvalidate

import elib
import yaml

from emiz.miz import Miz

# TODO: decode with "precise_float=True"

VERSION = None

MISSION_KEYS = [
    'coalition',
    'coalitions',
    'currentKey',
    'date',
    'L10N_descriptionBlueTask',
    'L10N_descriptionNeutralsTask',
    'L10N_descriptionRedTask',
    'L10N_descriptionText',
    'failures',
    'forcedOptions',
    'goals',
    'groundControl',
    'map',
    'maxDictId',
    'pictureFileNameB',
    'pictureFileNameN',
    'pictureFileNameR',
    'requiredModules',
    'result',
    'L10N_sortie',
    'start_time',
    'theatre',
    'trig',
    'triggers',
    'trigrules',
    'version',
    'weather',
]

REMAINING_KEYS = copy.copy(MISSION_KEYS)


class _Writer:
    @staticmethod
    def _write_to_disk(data: dict, path: Path):
        with path.open(mode='w', encoding='utf8') as stream:
            yaml.dump(data, stream, default_flow_style=False)

    @staticmethod
    def _build_output(miz, keys: typing.List[str]):
        output = {}
        for key in keys:
            output[key] = miz.mission[key]
            REMAINING_KEYS.remove(key)
        return output


# def _write(src: dict, path: Path, l10n, keys: typing.List[str] = None, debug=False):
#     output = {}
#     if keys is None:
#         keys = src.keys()
#     if debug:
#         print(keys)
#     for key in keys:
#         if debug:
#             print(key)
#         value = src[key]
#         output[key] = value
#         try:
#             REMAINING_KEYS.remove(key)
#         except ValueError:
#             pass
#     path.write_text(ujson.dumps(output, indent=2, ensure_ascii=False), encoding='utf8')


class _Paths:
    ext = '.json'

    def __init__(self, output_folder):
        self._miz = miz
        self._output_folder = elib.path.ensure_dir(output_folder, must_exist=False)
        self._output_folder.mkdir(exist_ok=True, parents=True)
        self.base_info = Path(output_folder, 'base_info.json')
        self.coalitions = Path(output_folder, 'coalitions.json')
        self.ground_control = Path(output_folder, 'ground_control.json')
        self.weather = Path(output_folder, 'weather.json')
        self.failures = Path(output_folder, 'failures.json')
        self.forced_options = Path(output_folder, 'forced_options.json')
        self.required_modules = Path(output_folder, 'required_modules.json')
        self.__coalitions = Path(output_folder, 'coalitions')
        self.coa_blue = Path(self.__coalitions, 'blue')
        self.coa_blue.mkdir(exist_ok=True, parents=True)
        self.coa_red = Path(self.__coalitions, 'red')
        self.coa_red.mkdir(exist_ok=True)
        self.map = Path(output_folder, 'map.json')
        self.folder_triggers = Path(output_folder, 'triggers')
        self.folder_triggers.mkdir(exist_ok=True)
        self.folder_zones = Path(output_folder, 'zones')
        self.folder_zones.mkdir(exist_ok=True)


class Decomposer:
    def __init__(self, miz, output_folder):
        self._dict = self._cleanup_dict(miz.mission.d, miz.l10n)
        self._version = miz.mission.d['version']
        self._check_keys(self._dict)
        self._l10n = miz.l10n
        self._resources = miz.map_res
        self._paths = _Paths(output_folder)
        self._remaining_keys = copy.deepcopy(MISSION_KEYS)
        self._write_ground_control()
        self._write_failures()
        self._write_map()
        self._write_coalitions()
        self._write_forced_otpions()
        self._write_zones()
        self._write_required_modules()
        self._write_weather()
        self._write_triggers()
        self._write_remaining()

    def _write_country_base_info(self, dict_: dict, base_path: Path):
        self._write(dict_, Path(base_path, 'base_info.yml'), ['name', 'id'])

    def _write_category_units(self, dict_: dict, base_path: Path):
        for unit in dict_:
            this_unit = dict_[unit]
            try:
                this_unit_name = this_unit['L10N_name']
            except KeyError:
                this_unit_name = this_unit['name']
            self._write(this_unit, Path(base_path, this_unit_name))

    def _write_country_categories(self, dict_: dict, base_path: Path):
        for category in ['plane', 'vehicle', 'static', 'helicopter', 'ship']:
            if category in dict_:
                category_folder = Path(base_path, category)
                category_folder.mkdir(exist_ok=True)
                self._write_category_units(dict_[category]['group'], category_folder)

    def _write_countries(self, country_dict: dict, base_path):
        for country in country_dict:
            this_country = country_dict[country]
            country_path = Path(base_path, this_country['name'])
            country_path.mkdir(exist_ok=True)
            self._write_country_base_info(this_country, country_path)
            self._write_country_categories(this_country, country_path)
            # _write(this_country, country_path, l10n)

    def _write_coa(self, dict_: dict, base_path):
        country_path = Path(base_path, 'country')
        country_path.mkdir(exist_ok=True, parents=True)
        self._write(
            dict_,
            Path(base_path, 'bullseye.yml'),
            ['bullseye'],
        )
        self._write(
            dict_,
            Path(base_path, 'nav_points.yml'),
            ['nav_points'],
        )
        self._write_countries(dict_['country'], country_path)

    def _write(self, src: dict, path: Path, keys: typing.List[str] = None, debug=False):
        output = {
            'version': self._version
        }
        if keys is None:
            keys = src.keys()
        if debug:
            print(keys)
        for key in keys:
            if debug:
                print(key)
            value = src[key]
            output[key] = value
            try:
                REMAINING_KEYS.remove(key)
            except ValueError:
                pass
        path.write_text(ujson.dumps(output, indent=2, ensure_ascii=False), encoding='utf8')

    @staticmethod
    def _cleanup_dict(dict_: dict, l10n: dict):
        output = {}
        for key in dict_:
            value = dict_[key]
            if isinstance(value, dict):
                output[key] = Decomposer._cleanup_dict(value, l10n)
            else:
                if isinstance(value, str) and value.startswith('DictKey_'):
                    try:
                        value = l10n[value]
                        output[f'L10N_{key}'] = value
                    except KeyError:
                        pass
                else:
                    output[key] = value
        return output

    @staticmethod
    def _check_keys(dict_: dict):
        for key in MISSION_KEYS:
            if key not in dict_:
                raise KeyError(key)

    def _write_triggers(self):
        trig = self._dict['trig']
        base_info_path = Path(self._paths.folder_triggers, 'base_info.yml')
        base_info = {
            'custom': trig['custom'],
            'customStartup': trig['customStartup'],
            'events': trig['events'],
        }
        self._write(base_info, base_info_path)
        for key in self._dict['trigrules']:
            trigger = self._dict['trigrules'][key]
            trigger_path = Path(self._paths.folder_triggers, f'{trigger["comment"]}.yml')
            # trigger_folder.mkdir(exist_ok=True)
            trigger['trig_actions'] = trig['actions'][key]
            trigger['trig_conditions'] = trig['conditions'][key]
            trigger['trig_flag'] = trig['flag'][key]
            if key in trig['func']:
                trigger['trig_func'] = trig['func'][key]
            elif key in trig['funcStartup']:
                trigger['trig_funcStartup'] = trig['funcStartup'][key]
            else:
                raise ValueError(f'func not found for {key}')
            self._write(trigger, trigger_path)
        REMAINING_KEYS.remove('trigrules')
        REMAINING_KEYS.remove('trig')

    def _write_weather(self):
        self._write(self._dict, self._paths.weather, ['weather'])

    def _write_required_modules(self):
        self._write(self._dict, self._paths.required_modules, ['requiredModules'])

    def _write_zones(self):
        zones = self._dict['triggers']['zones']
        for key in zones:
            zone = zones[key]
            self._write(zone, Path(self._paths.folder_zones, zone['name']))
        REMAINING_KEYS.remove('triggers')

    def _write_forced_otpions(self):
        self._write(self._dict, self._paths.forced_options, ['forcedOptions'])

    def _write_failures(self):
        self._write(self._dict, self._paths.failures, ['failures'])

    def _write_map(self):
        self._write(self._dict, self._paths.map, ['map'])

    def _write_remaining(self):
        self._write(self._dict, self._paths.base_info, list(REMAINING_KEYS))

    def _write_ground_control(self):
        self._write(self._dict, self._paths.ground_control, ['groundControl'])

    def _write_coalitions(self):
        self._write(self._dict, self._paths.coalitions, ['coalitions'])
        self._write_coa(self._dict['coalition']['blue'], self._paths.coa_blue)
        self._write_coa(self._dict['coalition']['red'], self._paths.coa_red)
        REMAINING_KEYS.remove('coalition')

        # def _write_base_info(self):
        #     keys = [
        #         'sortie',
        #         'version',
        #         'date', 'start_time',
        #         'descriptionBlueTask',
        #         'descriptionNeutralsTask',
        #         'descriptionRedTask',
        #         'descriptionText',
        #         'coalitions',
        #         'currentKey',
        #         'forcedOptions',
        #     ]
        #     _write(self._dict, self._paths.base_info, keys)


class Decomposer2:

    name_fields = ['callsignStr', 'name']

    def __init__(self, miz: Miz):
        self._dict = miz.mission.d
        self._l10n = miz.l10n
        self._map = miz.map_res
        self._version = self._dict['version']

    def _write_output_to_file(self, file: Path, output: dict):
        file.write_text(ujson.dumps(output, indent=2, ensure_ascii=False), encoding='utf8')

    def _decompose_list_dict(self, dict_: dict, output_folder: Path):
        count = 1
        order = {}
        for key in dict_:
            sub_dict = dict_[key]
            name = sub_dict['name']
            if name.startswith('DictKey_'):
                try:
                    name = self._l10n[name]
                except KeyError:
                    # TODO: l10n is missing a name !!!
                    pass
            if not name:
                name = str(key)
            order[count] = name
            count += 1
            subfolder = Path(output_folder, pathvalidate.sanitize_filename(name))
            self._decompose_dict(sub_dict, name, subfolder)
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
        if first_key and dict_ and isinstance(first_key, int) and isinstance(first_value, dict) and 'name' in first_value:
            self._decompose_list_dict(dict_, output_folder)
        else:
            is_single = True
            for key in dict_:
                value = dict_[key]
                if not key == 'properties' and isinstance(value, dict):
                    is_single = False
                    subfolder_name = pathvalidate.sanitize_filename(str(key))
                    subfolder = Path(output_folder, subfolder_name)
                    self._decompose_dict(value, key, subfolder)
                else:
                    output[key] = value
            if output:
                output['version'] = self._version
                _file_name = pathvalidate.sanitize_filename(str(key_name))
                if not is_single:
                    file = Path(output_folder, f'{_file_name}.json')
                else:
                    output_folder.rmdir()
                    file = Path(f'{output_folder}.json')
                    output['__single__'] = True
                self._write_output_to_file(file, output)

    def decompose(self, output_folder: Path):
        self._decompose_dict(self._dict, 'base_info', output_folder)



if __name__ == '__main__':
    import shutil
    test_file = './test/test_files/TRMT_6.4.3.miz'
    # test_file = './test/test_files/TRG_KA50.miz'
    test_folder = 'test_decompose'
    if Path(test_folder).exists():
        shutil.rmtree(test_folder)
    test_folder = Path(test_folder)
    with Miz(test_file) as miz_:
        # print(miz_.mission.d['weather'])
        # decomposer = Decomposer(miz_, output_folder)
        Decomposer2(miz_).decompose(test_folder)

# TODO: isolate triggers & trigrules (name value is "comment" on trigrules
# TODO: sanitize navpoints
