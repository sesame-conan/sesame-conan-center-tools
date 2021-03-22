import sys
import colorama
from colorama import Fore
import inspect

from sesame.commands.build import build_cmd
from sesame.commands.build_tools import build_tools_cmd
from sesame.commands.export import export_cmd
from sesame.commands.build_all import build_all_cmd
from sesame.commands.export_all import export_all_cmd


class Command(object):

    def version(self, *args):
        """Something about version"""
        print(Fore.GREEN + 'Display Version')

    def help(self, *args):
        """Something about help"""
        # TODO: Generate help from commands
        print(Fore.GREEN + 'Displays Help')
        commands = self._commands()
        for name, method in commands.items():
            print(name)
            print(f' {method.__doc__}')

    def export_all(self, *args):
        """Something about export"""
        print(Fore.LIGHTWHITE_EX + 'Exporting ...')
        export_all_cmd(args)

    def build_all(self, *args):
        """Something about build"""
        build_all_cmd(args)

    def export(self, *args):
        """Exports all versions of the given single recipe"""
        print(Fore.LIGHTWHITE_EX + f'Exporting ...')
        export_cmd(args)

    def build(self, *args):
        """Something about build"""
        build_cmd(args)

    def build_tools(self, *args):
        """Something about build_tools"""
        build_tools_cmd(args)

    def _commands(self):
        result = {}
        for m in inspect.getmembers(self, predicate=inspect.ismethod):
            method_name = m[0]
            if not method_name.startswith('_'):
                method = m[1]
                result[method_name.replace('_', '-')] = method
        return result

    def _run(self, args):
        if args:
            commands = self._commands()
            if args[0] in commands:
                command = args[0]
                method = commands[command]
                method(args[1:])
            else:
                print(Fore.LIGHTRED_EX + "Unknown command: " + Fore.LIGHTYELLOW_EX + f"`{' '.join(args)}`.")
                self.help()
        else:
            print(Fore.LIGHTRED_EX + "No command given.")
            self.help()


def _main(args):
    colorama.init(autoreset=True)
    command = Command()
    command._run(args)


def run():
    # TODO Add --help (will call help command above)
    # TODO Add --version (will call version command above)
    _main(sys.argv[1:])


if __name__ == '__main__':
    run()
