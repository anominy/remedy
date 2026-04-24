#  Copyright 2026 anominy
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# import re
import shutil
import sys
import subprocess

from pathlib import Path
from argparse import ArgumentParser
from more_or_less import paginate

_FAIL_CODE = 1
_SUCC_CODE = 0

_FAIL_MSG_PREFIX = '-- FAILURE: '
_SUCC_MSG_PREFIX = '-- SUCCESS: '

_PY_EXT = '.py'
_EXE_EXT = '.exe'
_QRC_EXT = '.qrc'
_ICO_EXT = '.ico'

_MAIN_PY_NAME = 'main'
_MAIN_EXE_NAME = 'Remedy'

_LICENSE_NAME = 'LICENSE'
_RESOURCES_NAME = 'resources'

_ROOT_DIR_PATH = Path(__file__).parent
_LICENSE_PATH = _ROOT_DIR_PATH / _LICENSE_NAME
_RES_DIR_PATH = _ROOT_DIR_PATH / 'res'
_SRC_DIR_PATH = _ROOT_DIR_PATH / 'src'
_OUT_DIR_PATH = _ROOT_DIR_PATH / 'out'
_BUILD_DIR_PATH = _ROOT_DIR_PATH / 'build'
_DIST_DIR_PATH = _BUILD_DIR_PATH / f'{_MAIN_PY_NAME}.dist'
_ICON_DIR_PATH = _RES_DIR_PATH / 'icons'
_REL_OUT_DIR_PATH = _OUT_DIR_PATH / 'release'
_DBG_OUT_DIR_PATH = _OUT_DIR_PATH / 'debug'
_QRC_RES_PATH = _RES_DIR_PATH / f'{_RESOURCES_NAME}{_QRC_EXT}'
_QRC_SRC_PATH = _SRC_DIR_PATH / f'{_RESOURCES_NAME}{_PY_EXT}'
_MAIN_SRC_PATH = _SRC_DIR_PATH / f'{_MAIN_PY_NAME}{_PY_EXT}'
_MAIN_DIST_PATH = _DIST_DIR_PATH / f'{_MAIN_EXE_NAME}{_EXE_EXT}'
_ICON_RES_PATH = _ICON_DIR_PATH / f'icon{_ICO_EXT}'

_QRCC_CMD_EXE = 'pyside6-rcc'
_QRCC_CMD_LST = [_QRCC_CMD_EXE, str(_QRC_RES_PATH.resolve()), '-o', str(_QRC_SRC_PATH.resolve())]

_APPC_CMD_EXE = 'nuitka'
_APPC_CMD_LST = [sys.executable, '-m', _APPC_CMD_EXE,
    '--quiet',
    '--standalone',
    # '--onefile',
    '--enable-plugin=pyside6',
    f'--output-dir={_BUILD_DIR_PATH.resolve()}',
    f'--output-filename={_MAIN_EXE_NAME}{_EXE_EXT}',
    f'--include-data-files={_LICENSE_PATH.resolve()}={_LICENSE_NAME}',
    '--include-windows-runtime-dlls=yes',
    f'--windows-icon-from-ico={_ICON_RES_PATH.resolve()}',
]
_APPC_CMD_REL_LST = ['--lto=yes', '--windows-console-mode=disable']
_APPC_CMD_DBG_LST = ['--lto=no', '--windows-console-mode=force']

def _p(*args, **kwargs):
    if args:
        text = f'{args[0]}{kwargs.get('sep', ' ').join(map(str, args[1:]))}'
    else:
        text = ''

    print(text, **kwargs)


def _f(*args):
    _p(_FAIL_MSG_PREFIX, *args, file=sys.stderr)
    return False


def _s(*args):
    _p(_SUCC_MSG_PREFIX, *args, file=sys.stdout)
    return True


# def _t(template, *args):
#     vals = list(args)
#
#     result = []
#     for x in template:
#         if vals:
#             y = vals.pop(0)
#         else:
#             y = None
#
#         if x is None:
#             if y is not None:
#                 result.append(y)
#             continue
#
#         if isinstance(x, str) and bool(re.search(r'\{(\d*)}', x)):
#             if y is None:
#                 raise ValueError('Not enough arguments for a template')
#
#             if isinstance(y, list):
#                 result.append(x.format(*y))
#                 continue
#
#             result.append(x.format(y))
#             continue
#
#         result.append(x)
#
#     if vals:
#         result.extend(vals)
#
#     return result


def _page_text(text, is_paged=None, pipe=None):
    class NewlineTrackerPipe:
        def __init__(self, pipe_):
            self.__pipe = pipe_
            self.__last = None

        def write(self, text_):
            self.__pipe.write(text_)
            self.__last = text_

        def flush(self):
            self.__pipe.flush()

        @property
        def is_last_newline(self):
            if self.__last is None:
                return None

            return self.__last.splitlines(keepends=True)[-1] \
                .endswith('\n')

    if is_paged is None:
        is_paged = False

    if pipe is None:
        pipe = sys.stdout

    if not is_paged:
        print(text, file=pipe)
        return

    original_pipe = pipe
    pipe = NewlineTrackerPipe(original_pipe)
    paginate(text, output=pipe)

    # noinspection PySimplifyBooleanCheck
    if pipe.is_last_newline is False:
        print(file=original_pipe)


def _print_license(is_paged=None):
    try:
        with open(_LICENSE_PATH, 'r') as file:
            license_text = file.read() \
                .rstrip()

        _page_text(license_text, is_paged)
        return True
    except Exception as ex:
        return _f(ex)


def _compile_qrc():
    try:
        subprocess.run(_QRCC_CMD_LST, check=True)

        cwd_path = Path.cwd()
        rel_qrc_res_path = _QRC_RES_PATH.relative_to(cwd_path)
        rel_qrc_src_path = _QRC_SRC_PATH.relative_to(cwd_path)
        return _s(rel_qrc_res_path, '->', rel_qrc_src_path)
    except Exception as ex:
        return _f(ex)


def _compile_exe(is_release=None):
    if is_release is None:
        is_release = False

    cwd_path = Path.cwd()
    rel_main_src_path = _MAIN_SRC_PATH.relative_to(cwd_path)
    if not _MAIN_SRC_PATH.exists():
        return _f('Could not find', rel_main_src_path)

    if is_release:
        compile_args = _APPC_CMD_REL_LST
    else:
        compile_args = _APPC_CMD_DBG_LST

    try:
        subprocess.run([*_APPC_CMD_LST, *compile_args, str(_MAIN_SRC_PATH.resolve())], check=True)

        if not _DIST_DIR_PATH.exists():
            rel_dist_dir_path = _DIST_DIR_PATH.relative_to(cwd_path)
            return _f('Could not find', rel_dist_dir_path)

        if not _MAIN_DIST_PATH.exists():
            rel_main_dist_path = _MAIN_DIST_PATH.relative_to(cwd_path)
            return _f('Could not compile', rel_main_dist_path)

        if is_release:
            out_dir_path = _REL_OUT_DIR_PATH
        else:
            out_dir_path = _DBG_OUT_DIR_PATH

        if out_dir_path.exists():
            shutil.rmtree(out_dir_path)
        out_dir_path.mkdir(parents=True, exist_ok=True)

        def log_copy(item_dir_path, dest_dir_path, item_path, dest_path):
            def e(base, path):
                rel_base_path = base.relative_to(cwd_path)
                rel_path_path = path.relative_to(cwd_path)

                base_parts = rel_base_path.parts
                path_parts = rel_path_path.parts
                if len(path_parts) - 1 <= len(base_parts):
                    return rel_path_path

                return Path(*base_parts, '...', path_parts[-1])

            item_path = Path(item_path)
            dest_path = Path(dest_path)

            result = shutil.copy2(item_path, dest_path)

            rel_item_path = e(item_dir_path, item_path)
            rel_dest_path = e(dest_dir_path, dest_path)
            _s(rel_item_path, '->', rel_dest_path)

            return result

        shutil.copytree(_DIST_DIR_PATH, out_dir_path, dirs_exist_ok=True, copy_function=\
            lambda item_path, dest_path: log_copy(_DIST_DIR_PATH, out_dir_path, item_path, dest_path))

        main_out_path = out_dir_path / f'{_MAIN_EXE_NAME}{_EXE_EXT}'
        rel_main_out_path = main_out_path.relative_to(cwd_path)
        return _s(rel_main_src_path, '->', rel_main_out_path)
    except Exception as ex:
        return _f(ex)


def _clean_out():
    try:
        if _OUT_DIR_PATH.exists():
            shutil.rmtree(_OUT_DIR_PATH)
            _OUT_DIR_PATH.mkdir(parents=True)
        return True
    except Exception as ex:
        return _f(ex)


def main():
    arg_parser = ArgumentParser(description='Build script for Remedy desktop application')

    arg_parser.add_argument(
        '-l', '--license',
        help='show the project license and exit',
        action='store_true'
    )

    arg_parser.add_argument(
        '-p', '--page',
        help='use paged output for large texts',
        action='store_true'
    )

    arg_parser.add_argument(
        '-q', '--qrc',
        help=f'compile {_QRC_RES_PATH.relative_to(Path.cwd())} with {_QRCC_CMD_EXE}',
        action='store_true'
    )

    arg_parser.add_argument(
        '-e', '--exe',
        help='compile this project with nuitka',
        action='store_true'
    )

    arg_parser.add_argument(
        '-r', '--release',
        help='use release flags for compilation of this project',
        action='store_true'
    )

    arg_parser.add_argument(
        '-c', '--clean',
        help='clean output directory of this project',
        action='store_true'
    )

    args = arg_parser.parse_args()
    if not any([args.license, args.qrc, args.exe, args.clean]):
        arg_parser.print_help()
        return _SUCC_CODE

    if args.license:
        is_success = _print_license(args.page)
        if not is_success:
            return _FAIL_CODE
        return _SUCC_CODE

    if args.clean:
        is_success = _clean_out()
        if not is_success:
            return _FAIL_CODE

    if args.qrc:
        is_success = _compile_qrc()
        if not is_success and args.exe:
            return _FAIL_CODE

    if args.exe:
        is_success = _compile_exe(args.release)
        if not is_success:
            return _FAIL_CODE

    return _SUCC_CODE


if __name__ == '__main__':
    sys.exit(main())
