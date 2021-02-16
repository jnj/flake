import argparse
import sys

from flake.util import config_logging
from flake.updart import updart
from flake.transcode import transcode


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

    p.add_argument(
        '-d',
        '--dry',
        help='dry run (does not make any changes)',
        action='store_true'
    )

    p.add_argument(
        '-v',
        '--verbose',
        help='log details to stdout',
        action='store_true'
    )

    subparsers = p.add_subparsers(
        title='subcommands',
        description='choose one of these commands to run',
        help='available subcommands'
    )

    clone_parser = subparsers.add_parser(
        'clone',
        help='make a copy of this path to another path'
    )

    clone_parser.add_argument('dest', help='destination path')
    clone_parser.add_argument('path', help='paths to clone')
    clone_parser.set_defaults(func=clone)

    updart_parser = subparsers.add_parser(
        'updart', help='update the embedded art in flac files'
    )

    updart_parser.add_argument(
        'path',
        help='path containing FLAC files',
        nargs='+'
    )

    updart_parser.add_argument(
        '-d',
        '--depth',
        help='dir max depth (negative -> unlimited)',
        type=int,
        default=-1
    )

    updart_parser.set_defaults(func=updart)

    transcode_parser = subparsers.add_parser(
        'transcode',
        help='transcode the audio to another format'
    )

    transcode_parser.add_argument(
        '-f',
        '--format',
        help='output format',
        default='mp3',
        choices=['mp3', 'ogg']
    )

    transcode_parser.add_argument(
        '-l',
        '--lstrip',
        help="dirs to strip from left of source files when storing. "
             "Example: /foo/bar/baz.flac -> /dest/bar/baz.mp3 when -l is 1",
        type=int
    )

    transcode_parser.add_argument('dest', help='destination path')
    transcode_parser.add_argument('path', help='source paths', nargs='+')
    transcode_parser.set_defaults(func=transcode)

    parsedargs = p.parse_args(sys.argv[1:])

    if hasattr(parsedargs, 'func'):
        parsedargs.func(parsedargs)
    else:
        p.print_usage()
        p.exit(status=1, message='Must call a subcommand')
