# coding=utf-8

import os

from pip.req import parse_requirements
from setuptools import find_packages, setup

requirements = [str(r.req) for r in
                parse_requirements('requirements.txt', session=False)]
test_requirements = [str(r.req) for r in
                     parse_requirements('requirements-dev.txt', session=False)]


def read_local_files(*file_paths: str) -> str:
    """
    Reads one or more text files and returns them joined together.

    A title is automatically created based on the file name.

    :param file_paths: list of files to aggregate

    """

    def _read_single_file(file_path):
        with open(file_path) as f:
            filename = os.path.splitext(file_path)[0]
            title = f'{filename}\n{"=" * len(filename)}'
            return '\n\n'.join((title, f.read()))

    return '\n' + '\n\n'.join(map(_read_single_file, file_paths))


setup(
    name='EMIZ',
    author='132nd-etcher',
    zip_safe=False,
    author_email='emiz@daribouca.net',
    platforms=['win32'],
    url=r'https://github.com/132nd-etcher/EMIZ',
    download_url=r'https://github.com/132nd-etcher/EMIZ/releases',
    description='Set of tools for the DCS mission builder',
    license='GPLv3',
    long_description=read_local_files('README.rst', 'CHANGELOG.rst'),
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    tests_require=test_requirements,
    python_requires='>=3.6',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Environment :: Win32 (MS Windows)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows 8',
        'Operating System :: Microsoft :: Windows :: Windows 8.1',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Games/Entertainment',
        'Topic :: Utilities',
    ],
)
