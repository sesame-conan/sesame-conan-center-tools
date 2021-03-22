import argparse
import os
import platform
import subprocess
import time
import yaml
from sesame import subprocess_run
from colorama import Fore, Back, Style


def build_cmd(args):
    """Builds a recipe"""
    parser = argparse.ArgumentParser(description=build_cmd.__doc__, prog='sesame build')
    parser.add_argument("recipe", help="Conan recipe that will be build")
    parser.add_argument("version", help="The version of the library that will be build")
    parser.add_argument("--user", '-u', help="Conan user that the package will be created under.", default='sesame')
    parser.add_argument("--channel", '-c', help="Conan channel that the package will be created under.",
                        default='testing')

    parser.add_argument("--android", help="builds for Android", default=False, action="store_true")
    parser.add_argument("--emscripten", help="builds for Emscripten", default=False, action="store_true")
    parser.add_argument("--linux", help="builds for Linux", default=False, action="store_true")
    parser.add_argument("--macos", help="builds for macOS", default=False, action="store_true")
    parser.add_argument("--ios", help="builds for iOS", default=False, action="store_true")
    parser.add_argument("--windows", help="builds for Windows", default=False, action="store_true")
    parser.add_argument("--uwp", help="builds for UWP", default=False, action="store_true")

    parser.add_argument("--keep-source",
                        help="Do not remove the source folder in the local cache, even if the recipe changed. Use this for testing purposes only.",
                        default=False,
                        action="store_true")

    parser.add_argument("--stacktrace",
                        help="Print stack trace when a conan cmd fails.",
                        default=False,
                        action="store_true")

    args = parser.parse_args(*args)
    _build(args)


def _build(args):
    sesame_root_dir = os.getcwd()
    recipes_root_dir = os.path.join(sesame_root_dir, "conan-center-index", "recipes")
    recipe_root_dir = os.path.join(recipes_root_dir, args.recipe)
    os.chdir(recipe_root_dir)

    if not os.path.exists('config.yml'):
        print(Fore.RED + Style.BRIGHT + f'{args.recipe} doesn\'t seem to have configuration file config.yml')
        # TODO: Throw exception?
        return

    # TODO: Learn how to handle failures `with open` statements
    with open('config.yml') as file:
        yml = yaml.load(file, Loader=yaml.FullLoader)
        versions = yml['versions']

    if args.version not in versions:
        print(Fore.RED + Style.BRIGHT + f'{args.recipe} doesn\'t seem to have version {args.version}')
        # TODO: Throw exception?
        return

    version = versions[args.version]
    recipe_version_dir = os.path.join(recipe_root_dir, version['folder'])
    os.chdir(recipe_version_dir)

    base_cmd = ['conan', 'create', '.', 'orhun/deleteme']

    if args.keep_source:
        base_cmd.append('--keep-source')

    if platform.system() == 'Linux':
        base_cmd += ['-pr:b', f'{sesame_root_dir}/profiles/LinuxBuild.profile']
    elif platform.system() == 'Windows':
        base_cmd += ['-pr:b', f'{sesame_root_dir}/profiles/WindowsBuild.profile']
    elif platform.system() == 'Darwin':
        base_cmd += ['-pr:b', f'{sesame_root_dir}/profiles/macOSBuild.profile']

    if args.android:
        platform_cmd = base_cmd + ['-pr:h', f'{sesame_root_dir}/profiles/AndroidHost.profile']

    cmd = platform_cmd + ['-s:h', 'arch=armv8']
    subprocess_run(cmd, args.stacktrace)

    print(os.getcwd())
    os.chdir(sesame_root_dir)
    print(os.getcwd())
