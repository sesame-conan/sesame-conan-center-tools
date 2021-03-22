import argparse
import os
import platform
import subprocess
import time
import yaml
from sesame import subprocess_run
from sesame.commands.export import export_cmd
from colorama import Fore, Back, Style


def build_all_cmd(args):
    """Builds all recipes listed in packages.yml"""
    parser = argparse.ArgumentParser(description=build_all_cmd.__doc__, prog='sesame build')

    platforms = parser.add_argument_group("platforms")
    platforms.add_argument("--android", help="builds for Android", default=False, action="store_true")
    platforms.add_argument("--emscripten", help="builds for Emscripten", default=False, action="store_true")
    platforms.add_argument("--linux", help="builds for Linux", default=False, action="store_true")
    platforms.add_argument("--macos", help="builds for macOS", default=False, action="store_true")
    platforms.add_argument("--ios", help="builds for iOS", default=False, action="store_true")
    platforms.add_argument("--windows", help="builds for Windows", default=False, action="store_true")
    platforms.add_argument("--uwp", help="builds for UWP", default=False, action="store_true")

    parser.add_argument("--upload",
                        help="Upload after building.",
                        type=str,
                        default=None)

    parser.add_argument("--stacktrace",
                        help="Print stack trace when a conan cmd fails.",
                        default=False,
                        action="store_true")

    args = parser.parse_args(*args)
    if args.android or args.emscripten or args.linux or args.macos or args.ios or args.windows:
        _build_all(args)
    else:
        print(Fore.RED + Style.BRIGHT + 'Specify at least one platform to build.')


def _build_all(args):
    _export_deps(args)

    sesame_root_dir = os.getcwd()

    if not os.path.exists('packages.yml'):
        print(Fore.RED + Style.BRIGHT + f'{args.recipe} doesn\'t seem to have configuration file packages.yml')
        # TODO: Throw exception?
        return

    with open('packages.yml') as file:
        yml = yaml.load(file, Loader=yaml.FullLoader)

    packages = {}
    for package in yml:
        recipe = package["name"]
        version = package["version"]
        recipe_root_dir = os.path.join(sesame_root_dir, "conan-center-index", "recipes", recipe)
        os.chdir(recipe_root_dir)

        if not os.path.exists('config.yml'):
            print(Fore.RED + Style.BRIGHT + f'{args.recipe} doesn\'t seem to have configuration file config.yml')
            # TODO: Throw exception?
            return

        # TODO: Learn how to handle failures `with open` statements
        with open('config.yml') as file:
            yml = yaml.load(file, Loader=yaml.FullLoader)
            versions = yml['versions']

        if version not in versions:
            print(Fore.RED + Style.BRIGHT + f'{recipe} doesn\'t seem to have version {version}')
            print(versions)
            print(versions[version])
            # TODO: Throw exception?
            return

        version_dir = versions[version]
        recipe_version_dir = os.path.join(recipe_root_dir, version_dir['folder'])

        packages[recipe] = [version, recipe_version_dir]

    for name, info in packages.items():
        version = info[0]
        recipe_version_dir = info[1]
        os.chdir(recipe_version_dir)
        cmd = ['conan', 'export', '.', f'{name}/{version}@']
        subprocess_run(cmd, args.stacktrace)

    # for name, info in packages.items():
    #     version = info[0]
    #     recipe_version_dir = info[1]
    #     os.chdir(recipe_version_dir)
    #     cmd = ['conan', 'info', f'{name}/{version}@', '--only', 'None', '-s', 'os=Android', '-s', 'os.api_level=28',
    #            '-s', 'compiler=clang', '-s', 'compiler.version=9', '-s', 'compiler.libcxx=libc++']
    #     print(Fore.YELLOW + Style.BRIGHT + ' '.join(cmd))
    #     subprocess.run(cmd)

    os.chdir(sesame_root_dir)

    template = """
from conans import ConanFile


class SomethingConan(ConanFile):
    name = "something"
    version = "1.0"
    settings = "os", "compiler", "build_type", "arch"
    description = "<Description of Something here>"
    url = "None"
    license = "None"
    author = "None"
    topics = None


    def requirements(self):
"""
    with open('conanfile.py', 'w') as file:
        file.write(template)
        for name, info in packages.items():
            version = info[0]
            file.write(f'        self.requires("{name}/{version}")\n')

    # subprocess.run(['conan', 'info', '.', '--only', 'None', '-s', 'os=Android', '-s', 'os.api_level=28', '-s', 'compiler=clang', '-s', 'compiler.version=9', '-s', 'compiler.libcxx=libc++'])
    base_cmd = ['conan', 'create', './conanfile.py', '--keep-source', '--build', 'missing']

    if platform.system() == 'Linux':
        base_cmd += ['-pr:b', 'profiles/LinuxBuild.profile']
    elif platform.system() == 'Windows':
        base_cmd += ['-pr:b', 'profiles/WindowsBuild.profile']
    elif platform.system() == 'Darwin':
        base_cmd += ['-pr:b', 'profiles/macOSBuild.profile']

    build_types = ['Debug']  # , 'RelWithDebInfo']

    if args.android:
        arches = ['armv8']  # , 'x86_64']
        platform_cmd = base_cmd + ['-pr:h', 'profiles/AndroidHost.profile']

        for build_type in build_types:
            build_type_cmd = platform_cmd + ['-s:h', f'build_type={build_type}']
            for arch in arches:
                cmd = build_type_cmd + ['-s:h', f'arch={arch}']
                subprocess_run(cmd, args.stacktrace)
    else:
        print(Fore.RED + Style.BRIGHT + 'No platform given.')
        return

    if args.upload:
        for name, info in packages.items():
            version = info[0]
            cmd = ['conan', 'upload', '--confirm', '--all', '--remote', args.upload, f'{name}/{version}']
            subprocess_run(cmd, args.stacktrace)


def _export_deps(args):
    with open('dependencies.yml') as file:
        yml = yaml.load(file, Loader=yaml.FullLoader)

    if not yml:
        yml = []

    export_args = []
    if args.stacktrace:
        export_args += ['--stacktrace']
    for dep in yml:
        export_cmd(([dep, *export_args],))
