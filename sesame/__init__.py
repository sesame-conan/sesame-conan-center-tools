import subprocess
import sys
import traceback
from inspect import getframeinfo, stack
from colorama import Fore, Style


def subprocess_run(cmd, is_stacktrace):
    caller = getframeinfo(stack()[1][0])
    print(f'{Fore.WHITE}> {Fore.YELLOW}{Style.BRIGHT}{" ".join(cmd)}', end=" ")
    print(f'{Fore.LIGHTWHITE_EX}=> called from File "{caller.filename}", line {caller.lineno}')
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        if is_stacktrace:
            traceback.print_stack(limit=2)
        sys.exit(42)
