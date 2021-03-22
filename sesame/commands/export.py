import argparse
import os
import platform
import subprocess
import sys
import time
import traceback
import yaml
from colorama import Fore, Back, Style
from sesame import subprocess_run

def export_cmd(args):
    """Exports all versions of the given single recipe in conan-center-index"""
    parser = argparse.ArgumentParser(description=export_cmd.__doc__, prog='sesame export')
    parser.add_argument("reference", help="Conan reference (i.e. recipe/version, zlib/1.2.11) that will be exported.")

    parser.add_argument("--stacktrace", help="Print stack trace when a conan cmd fails.", default=False, action="store_true")
    args = parser.parse_args(*args)
    _export(args)


def _export(args):
    sesame_root_dir = os.getcwd()
    name, version = args.reference.split('/')
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
    cmd = ['conan', 'export', '.', f'{name}/{version}@']
    subprocess_run(cmd, args.stacktrace)

    os.chdir(sesame_root_dir)
