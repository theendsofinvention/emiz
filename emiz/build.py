# coding=utf-8
"""
Collections of tools to build a python app
"""
import importlib
import os
import re
import shlex
import shutil
import subprocess
import sys
import typing
import webbrowser
from contextlib import contextmanager
from json import loads

import click
from pkg_resources import DistributionNotFound, get_distribution

# noinspection SpellCheckingInspection
PYINSTALLER_NEEDED_VERSION = '3.3.dev0+g2fcbe0f'
PACKAGE_NAME = 'emiz'
DOC_REPO = r'https://github.com/132nd-etcher/emiz-doc.git'
DOC_FOLDER = './emiz-doc'


@contextmanager
def cd(path):
    """
    Context to temporarily change the working directory

    Args:
        path: working directory to cd into
    """
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


def repo_is_dirty(ctx) -> bool:
    """
    Checks if the current repository contains uncommitted or untracked changes

    Returns: true if the repository is clean
    """
    out, _, _ = do_ex(ctx, ['git', 'status', '--porcelain', '--untracked-files=no'])
    return bool(out)


def ensure_repo():
    """
    Makes sure the current working directory is a Git repository.
    """
    if not os.path.exists('.git') or not os.path.exists(PACKAGE_NAME):
        click.secho('This command is meant to be ran in a Git repository.\n'
                    'You can clone the repository by running:\n\n'
                    f'\tgit clone https://github.com/132nd-etcher/{PACKAGE_NAME}.git\n\n'
                    'Then cd into it and try again.',
                    fg='red', err=True)
        exit(-1)


def ensure_module(ctx, module_name: str, import_name: str = None):
    """
    Makes sure that a module is importable.

    In case the module cannot be found, print an error and exit.

    Args:
        import_name: name to use while trying to import
        module_name: name of the module if install is needed
    """
    if import_name is None:
        import_name = module_name
    try:
        importlib.import_module(import_name)
    except ModuleNotFoundError:
        do(ctx, ['pip', 'install', module_name])


def find_executable(executable: str, path: str = None) -> typing.Union[str, None]:  # noqa: C901
    # noinspection SpellCheckingInspection
    """
    https://gist.github.com/4368898

    Public domain code by anatoly techtonik <techtonik@gmail.com>

    Programmatic equivalent to Linux `which` and Windows `where`

    Find if ´executable´ can be run. Looks for it in 'path'
    (string that lists directories separated by 'os.pathsep';
    defaults to os.environ['PATH']). Checks for all executable
    extensions. Returns full path or None if no command is found.

    Args:
        executable: executable name to look for
        path: root path to examine (defaults to system PATH)

    """

    if not executable.endswith('.exe'):
        executable = f'{executable}.exe'

    if executable in find_executable.known_executables:  # type: ignore
        return find_executable.known_executables[executable]  # type: ignore

    click.secho(f'looking for executable: {executable}', fg='green', nl=False)

    if path is None:
        path = os.environ['PATH']
    paths = [os.path.abspath(os.path.join(sys.exec_prefix, 'Scripts'))] + path.split(os.pathsep)
    if os.path.isfile(executable):
        executable_path = os.path.abspath(executable)
    else:
        for path_ in paths:
            executable_path = os.path.join(path_, executable)
            if os.path.isfile(executable_path):
                break
        else:
            click.secho(f' -> not found', fg='red', err=True)
            return None

    find_executable.known_executables[executable] = executable_path  # type: ignore
    click.secho(f' -> {click.format_filename(executable_path)}', fg='green')
    return executable_path


find_executable.known_executables = {}  # type: ignore


def do_ex(ctx: click.Context, cmd: typing.List[str], cwd: str = '.') -> typing.Tuple[str, str, int]:
    """
    Executes a given command

    Args:
        ctx: Click context
        cmd: command to run
        cwd: working directory (defaults to ".")

    Returns: stdout, stderr, exit_code

    """

    def _popen_pipes(cmd_, cwd_):
        def _always_strings(env_dict):
            """
            On Windows and Python 2, environment dictionaries must be strings
            and not unicode.
            """
            env_dict.update(
                (key, str(value))
                for (key, value) in env_dict.items()
            )
            return env_dict

        return subprocess.Popen(
            cmd_,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(cwd_),
            env=_always_strings(
                dict(
                    os.environ,
                    # try to disable i18n
                    LC_ALL='C',
                    LANGUAGE='',
                    HGPLAIN='1',
                )
            )
        )

    def _ensure_stripped_str(_, str_or_bytes):
        if isinstance(str_or_bytes, str):
            return '\n'.join(str_or_bytes.strip().splitlines())
        else:
            return '\n'.join(str_or_bytes.decode('utf-8', 'surogate_escape').strip().splitlines())

    exe = find_executable(cmd.pop(0))
    if not exe:
        exit(-1)
    cmd.insert(0, exe)
    click.secho(f'{cmd}', nl=False, fg='magenta')
    p = _popen_pipes(cmd, cwd)
    out, err = p.communicate()
    click.secho(f' -> {p.returncode}', fg='magenta')
    return _ensure_stripped_str(ctx, out), _ensure_stripped_str(ctx, err), p.returncode


def do(
    ctx: click.Context,
    cmd: typing.List[str],
    cwd: str = '.',
    mute_stdout: bool = False,
    mute_stderr: bool = False,
    # @formatter:off
    filter_output: typing.Union[None, typing.Iterable[str]]=None
    # @formatter:on
) -> str:
    """
    Executes a command and returns the result

    Args:
        ctx: click context
        cmd: command to execute
        cwd: working directory (defaults to ".")
        mute_stdout: if true, stdout will not be printed
        mute_stderr: if true, stderr will not be printed
        filter_output: gives a list of partial strings to filter out from the output (stdout or stderr)

    Returns: stdout
    """

    def _filter_output(input_):

        def _filter_line(line):
            # noinspection PyTypeChecker
            for filter_str in filter_output:
                if filter_str in line:
                    return False
            return True

        if filter_output is None:
            return input_
        return '\n'.join(filter(_filter_line, input_.split('\n')))

    if not isinstance(cmd, (list, tuple)):
        cmd = shlex.split(cmd)

    out, err, ret = do_ex(ctx, cmd, cwd)
    if out and not mute_stdout:
        click.secho(f'{_filter_output(out)}', fg='cyan')
    if err and not mute_stderr:
        click.secho(f'{_filter_output(err)}', fg='red')
    if ret:
        click.secho(f'command failed: {cmd}', err=True, fg='red')
        exit(ret)
    return out


def _write_requirements(ctx: click.Context, packages_list, outfile, prefix_list=None):
    with open('temp', 'w') as source_file:
        source_file.write('\n'.join(packages_list))
    packages, _, ret = do_ex(
        ctx,
        [
            'pip-compile',
            '--index',
            '--upgrade',
            '--annotate',
            '--no-header',
            '-n',
            'temp'
        ]
    )
    os.remove('temp')
    with open(outfile, 'w') as req_file:
        if prefix_list:
            for prefix in prefix_list:
                req_file.write(f'{prefix}\n')
        for package in packages.splitlines():
            req_file.write(f'{package}\n')


def _install_pyinstaller(ctx: click.Context, force: bool = False):
    """
    Installs pyinstaller package from a custom repository

    The latest official master branch of Pyinstaller does not work with the version of Python I'm using at this time

    Args:
        ctx: lick context (passed automatically by Click)
        force: uses "pip --upgrade" to force the installation of this specific version of PyInstaller
    """
    repo = r'git+https://github.com/132nd-etcher/pyinstaller.git@develop#egg=pyinstaller==3.3.dev0+g2fcbe0f'
    if force:
        do(ctx, ['pip', 'install', '--upgrade', repo])
    else:
        do(ctx, ['pip', 'install', repo])


def _get_version():
    try:
        return get_distribution(PACKAGE_NAME).version
    except DistributionNotFound:
        return 'not installed'


# noinspection PyUnusedLocal
def _print_version(ctx: click.Context, _, value):
    if not value or ctx.resilient_parsing:
        return

    ensure_repo()

    click.secho(_get_version(), fg='green')
    exit(0)


# @click.group(invoke_without_command=True)
@click.group(chain=True)
@click.option('-v', '--version',
              is_flag=True, is_eager=True, expose_value=False, callback=_print_version, default=False,
              help='Print version and exit')
@click.pass_context
def cli(ctx):
    """
    This is a tool that handles all the tasks to build a Python application

    This tool is installed as a setuptools entry point, which means it should be accessible from your terminal once
    this application is installed in develop mode.

    Just activate your venv and type the following in whatever shell you fancy:
    """
    ensure_repo()
    ctx.obj = {
        'version': _get_version()
    }
    click.secho(ctx.obj['version'], fg='green')

    # if ctx.invoked_subcommand is None:
    #     Checks.safety(ctx)
    #     Checks.flake8(ctx)
    #     Checks.pytest(ctx)
    #     # Checks.pylint()  # TODO
    #     # Checks.prospector()  # TODO
    #     HouseKeeping.compile_qt_resources(ctx)
    #     HouseKeeping.write_changelog(ctx, commit=True)
    #     HouseKeeping.write_requirements(ctx)
    #     Make.install_pyinstaller(ctx)
    #     Make.freeze(ctx)
    #     Make.patch_exe(ctx)
    #     Make.build_doc(ctx)


@cli.command()
@click.option('--prod/--no-prod', default=True, help='Whether or not to write "requirement.txt"')
@click.option('--test/--no-test', default=True, help='Whether or not to write "requirement-test.txt"')
@click.option('--dev/--no-dev', default=True, help='Whether or not to write "requirement-dev.txt"')
@click.pass_context
def reqs(ctx: click.Context, prod, test, dev):
    """
    Write requirements files
    """
    if not find_executable('pip-compile'):
        click.secho('Missing module "pip-tools".\n'
                    'Install it manually with: "pip install pip-tools"\n'
                    'Or install all dependencies with: "pip install -r requirements-dev.txt"',
                    err=True, fg='red')
        exit(-1)
    if prod:
        sys.path.insert(0, os.path.abspath('.'))
        from setup import install_requires
        _write_requirements(
            ctx,
            packages_list=install_requires,
            outfile='requirements.txt'
        )
        sys.path.pop(0)
    if test:
        """Writes requirements-test.txt"""
        from setup import test_requires
        _write_requirements(
            ctx,
            packages_list=test_requires,
            outfile='requirements-test.txt',
            prefix_list=['-r requirements.txt']
        )
    if dev:
        """Writes requirements-dev.txt"""
        from setup import dev_requires
        _write_requirements(
            ctx,
            packages_list=dev_requires,
            outfile='requirements-dev.txt',
            prefix_list=['-r requirements.txt', '-r requirements-test.txt']
        )


@cli.command()
@click.pass_context
def chglog(ctx):
    """
    Writes the changelog

    Returns:
        bool: returns true if changes have been committed to the repository
    """
    ensure_module(ctx, 'gitchangelog')
    find_executable('git')
    """
    Write the changelog using "gitchangelog" (https://github.com/vaab/gitchangelog)
    """
    changelog = do(ctx, ['gitchangelog'], mute_stdout=True)
    with open('CHANGELOG.rst', mode='w') as f:
        f.write(re.sub(r'(\s*\r\n){2,}', '\r\n', changelog))


@cli.command()
@click.pass_context
def pytest(ctx):
    """
    Runs Pytest (https://docs.pytest.org/en/latest/)
    """
    ensure_module(ctx, 'pytest')
    do(ctx, ['pytest'])


@cli.command()
@click.pass_context
def flake8(ctx):
    """
    Runs Flake8 (http://flake8.pycqa.org/en/latest/)
    """
    ensure_module(ctx, 'flake8')
    do(ctx, ['flake8'])


@cli.command()
@click.pass_context
def prospector(ctx):
    """
    Runs Landscape.io's Prospector (https://github.com/landscapeio/prospector)

    This includes flake8 & Pylint
    """
    ensure_module(ctx, 'prospector')
    do(ctx, ['prospector'])


@cli.command()
@click.pass_context
@click.argument('src', type=click.Path(exists=True), default=PACKAGE_NAME)
@click.option('-r', '--reports', is_flag=True, help='Display full report')
@click.option('-f', '--format', 'format_',
              type=click.Choice(['text', 'parseable', 'colorized', 'json']), default='colorized')
def pylint(ctx, src, reports, format_):
    """
    Analyze a given python SRC (module or package) with Pylint (SRC must exist)

    Default module: PACKAGE_NAME
    """
    ensure_module(ctx, 'pylint')
    cmd = ['pylint', src, f'--output-format={format_}']
    if reports:
        cmd.append('--reports=y')
    do(ctx, cmd)


@cli.command()
@click.pass_context
def safety(ctx):
    """
    Runs Pyup's Safety tool (https://pyup.io/safety/)
    """
    ensure_module(ctx, 'safety')
    do(ctx, ['safety', 'check', '--bare'])


@cli.command()
@click.pass_context
def autopep8(ctx):
    """
    Runs Pyup's Safety tool (https://pyup.io/safety/)
    """
    ensure_module(ctx, 'safety')
    do(ctx, ['autopep8', '-r', '--in-place', '.'])


@cli.command()
@click.option('-s', '--show', is_flag=True, help='Show the doc in browser')
@click.option('-c', '--clean', is_flag=True, help='Clean build')
@click.option('-p', '--publish', is_flag=True, help='Upload doc')
@click.pass_context
def doc(ctx, show, clean, publish):
    """
    Builds the documentation using Sphinx (http://www.sphinx-doc.org/en/stable)
    """
    if clean and os.path.exists('./doc/html'):
        shutil.rmtree('./doc/html')
    if os.path.exists('./doc/api'):
        shutil.rmtree('./doc/api')
    do(ctx, [
        'sphinx-apidoc',
        PACKAGE_NAME,
        '-o', 'doc/api',
        '-H', f'{PACKAGE_NAME} API',
        '-A', '132nd-etcher',
        '-V', f'{ctx.obj["semver"]}\n({ctx.obj["pep440"]})',
        # '-P',
        '-f',
    ])
    do(ctx, [
        'sphinx-build',
        '-b',
        'html',
        'doc',
        'doc/html'
    ])
    if show:
        webbrowser.open_new_tab(f'file://{os.path.abspath("./doc/html/index.html")}')
    if publish:
        output_filter = [
            'warning: LF will be replaced by CRLF',
            'The file will have its original line endings',
            'Checking out files:'
        ]
        if not os.path.exists(f'./{PACKAGE_NAME}-doc'):
            do(ctx, ['git', 'clone', DOC_REPO], filter_output=output_filter)
        with cd(DOC_FOLDER):
            do(ctx, ['git', 'pull'])
            if os.path.exists('./docs'):
                shutil.rmtree('./docs')
            shutil.copytree('../doc/html', './docs')
            do(ctx, ['git', 'add', '.'], filter_output=output_filter)
            do(ctx, ['git', 'commit', '-m', 'automated doc build'], filter_output=output_filter)
            do(ctx, ['git', 'push'], filter_output=output_filter)


@cli.command()
@click.pass_context
def pre_push(ctx):
    """
    This is meant to be used as a Git pre-push hook
    """
    ctx.invoke(autopep8)
    ctx.invoke(reqs)
    ctx.invoke(chglog)
    ctx.invoke(flake8)
    ctx.invoke(safety)
    if repo_is_dirty(ctx):
        click.secho('Repository is dirty', err=True, fg='red')
        exit(-1)
    click.secho('All good!', fg='green')


@cli.command()
@click.pass_context
def test_local_build(ctx):
    """
    This is meant to be used as a Git pre-push hook
    """
    ctx.invoke(flake8)
    ctx.invoke(pytest)
