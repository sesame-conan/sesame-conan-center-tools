import argparse
import os
import platform
import subprocess
import time
import yaml
from sesame import subprocess_run
from colorama import Fore, Back, Style


def export_all_cmd(args):
    """Exports all recipes, all versions in conan-center-index"""
    parser = argparse.ArgumentParser(description=export_all_cmd.__doc__, prog='sesame export_all')
    args = parser.parse_args(*args)
    _export_all(args)


def _export_all(args):
    # TODO: This is a VERY LONG running command ~1hr. Ask confirmation and progress bar!
    sesame_root_dir = os.getcwd()
    recipes_root_dir = os.path.join(sesame_root_dir, "conan-center-index", "recipes")

    recipes = os.listdir(recipes_root_dir)
    for recipe in recipes:
        recipe_root_dir = os.path.join(recipes_root_dir, recipe)
        os.chdir(recipe_root_dir)

        try:
            with open('config.yml') as file:
                yml = yaml.load(file, Loader=yaml.FullLoader)
                versions = yml['versions']
        except IOError as e:
            print(Fore.RED + Style.BRIGHT + f'{recipe_root_dir} => {str(e)}')
            # TODO: Store these and report them at the end. They are lost in the output!
            continue

        for version in versions:
            version_dir = versions[version]
            recipe_version_dir = os.path.join(recipe_root_dir, version_dir['folder'])
            os.chdir(recipe_version_dir)
            cmd = ['conan', 'export', '.', f'{recipe}/{version}@']
            subprocess_run(cmd, args.stacktrace)

    os.chdir(sesame_root_dir)
