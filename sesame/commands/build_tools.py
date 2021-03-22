import argparse
import os
import platform
import subprocess
import time
import yaml
from sesame import subprocess_run
from sesame.commands.export import export_cmd
from colorama import Fore, Back, Style


def build_tools_cmd(args):
    """Builds all recipes listed in tools.yml"""
    parser = argparse.ArgumentParser(description=build_tools_cmd.__doc__, prog='sesame build-tools')

    parser.add_argument("--upload",
                        help="Upload after building.",
                        type=str,
                        default=None)

    parser.add_argument("--stacktrace",
                        help="Print stack trace when a conan cmd fails.",
                        default=False,
                        action="store_true")

    args = parser.parse_args(*args)
    #if platform.system() == 'Windows':
    #    _build_windows_tools(args)

    _build_tools(args, 'tools.yml')


def _build_windows_tools(args):
    _build_tools(args, 'windows-tools.yml')


def _build_tools(args, tools_yml):
    if not os.path.exists(tools_yml):
        print(Fore.RED + Style.BRIGHT + f'{args.recipe} doesn\'t seem to have configuration file {tools_yml}')
        # TODO: Throw exception?
        return

    with open(tools_yml) as file:
        yml = yaml.load(file, Loader=yaml.FullLoader)

    for tool in yml:
        sesame_root_dir = os.getcwd()
        name, version = tool.split('/')
        recipes_root_dir = os.path.join(sesame_root_dir, "conan-center-index", "recipes")
        recipe_root_dir = os.path.join(recipes_root_dir, name)
        os.chdir(recipe_root_dir)

        try:
            with open('config.yml') as file:
                yml = yaml.load(file, Loader=yaml.FullLoader)
                versions = yml['versions']
        except IOError as e:
            print(Fore.RED + Style.BRIGHT + f'{recipe_root_dir} => {str(e)}')
            return

        version_dir = versions[version]
        recipe_version_dir = os.path.join(recipe_root_dir, version_dir['folder'])
        os.chdir(recipe_version_dir)
        cmd = ['conan', 'create', '.', f'{name}/{version}@']
        subprocess_run(cmd, args.stacktrace)

        if args.upload:
            cmd = ['conan', 'upload', '--confirm', '--all', '--remote', args.upload, f'{name}/{version}']
            subprocess_run(cmd, args.stacktrace)

        os.chdir(sesame_root_dir)
