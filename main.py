import argparse
import sys

from flake.util import config_logging
from flake.updart import updart


def clone(args):
    pass


if __name__ == '__main__':
    config_logging()
    desc = """
    Flake: a tool for managing a local FLAC music collection.
    """
    p = argparse.ArgumentParser(
        prog='flake',
        description=desc,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    p.add_argument('-d', '--dry',
                   help='dry run (does not make any changes)',
                   action='store_true')
    p.add_argument('-v', '--verbose',
                   help='log details to stdout',
                   action='store_true')

    subparsers = p.add_subparsers(
        title='subcommands',
        description='choose one of these commands to run',
        help='available subcommands')
    clone_parser = subparsers.add_parser(
        'clone', help='make a copy of this path to another path')
    clone_parser.add_argument('dest', help='destination path')
    clone_parser.add_argument('path', help='paths to clone')
    clone_parser.set_defaults(func=clone)

    updart_parser = subparsers.add_parser(
        'updart', help='update the embedded art in flac files'
    )
    updart_parser.add_argument('path',
                               help='path containing FLAC files',
                               nargs='+')
    updart_parser.add_argument('-d', '--depth',
                               help='dir max depth (negative -> unlimited)',
                               type=int,
                               default=-1)
    updart_parser.set_defaults(func=updart)

    parsedargs = p.parse_args(sys.argv[1:])
    if parsedargs.func:
        parsedargs.func(parsedargs)
    else:
        p.print_usage()
        sys.exit(1)
