#!/usr/bin/python3
"""
Usage:
    crone [--help | -h] [--version | -v] <command> [<args>...]

Commands:
    enhance         Calculate cost of enhancing gear

See 'crone <command> --help' for more information on a specific command.                 
                    
Options:
    -h, --help      Display the help page
    -v, --version   Display the currently installed version

"""
import importlib
import os.path
import subprocess

from docopt import docopt 

def main() :
    args = docopt (__doc__,
                    version="crone version 0.0.1",
                    options_first=True)

    if args["<command>"] in "enhance".split(" "):
        # In case <command> is a valid command
        # The choice is to import the required parser module and pass the options to it
        # Motivation: decouple implementation of the parser from the implementation
        # of the specific functionalities in case I want to use them elsewhere
        full_module_name = ".".join(["lib", args["<command>"], args["<command>"] + "_parser"])
        imported = importlib.import_module(full_module_name)
        args_for_imported_module = [args["<command>"]] + args["<args>"]
        new_args = docopt(imported.__doc__, argv=args_for_imported_module)
        imported.main(**new_args)
    elif args["<command>"] in ["help", None]:
        # In case there are no
        exit(subprocess.call(["python", "crone.py", "--help"]))
    else:
        exit("{} is not a crone command. See 'crone help'.".format(args["<command>"]))


if __name__ == "__main__":
    main()
    
