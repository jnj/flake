import argparse
import sys

from flake.util import config_logging
from flake.updart import updart
from flake.transcode import transcode
from flake.noart import noart
from flake.renum import renum
from flake.tag import tag
from flake.clone import clone

if __name__ == '__main__':
    config_logging()
    desc = """
    Flake: a tool for managing a local FLAC music collection.
    """
    p = argparse.ArgumentParser(
        prog='flake', description=desc,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    p.add_argument('-d', '--dry', help='dry run (does not make any changes)',
                   action='store_true')
    p.add_argument('-v', '--verbose', help='log details to stdout',
                   action='store_true')

    subp = p.add_subparsers(
        title='subcommands', description='choose one of these commands to run',
        help='available subcommands')

    tagp = subp.add_parser('tag', help='set tags')
    tagp.add_argument('-a', '--artist', help='set artist')
    tagp.add_argument('-al', '--album', help='set album')
    tagp.add_argument('-aa', '--aartist', help='set album artist')
    tagp.add_argument('-g', '--genre', help='set genre')
    tagp.add_argument('-d', '--date', help='set date')
    tagp.add_argument('-t', '--title', help='set title')
    tagp.add_argument('-dn', '--discno', help='disc number')
    tagp.add_argument('-tn', '--trackno', help='track number')
    tagp.add_argument('-r', '--remove', help='remove the tags',
                      action='store_const', const=True, default=False)
    tagp.add_argument('-ra', '--remove-all', dest='removeall',
                      help='remove all tags before setting any',
                      action='store_const', const=True, default=False)
    tagp.add_argument('-s', '--show', help='show tag values',
                      action='store_const', const=True, default=False)
    tagp.add_argument('file', help='files', nargs='+')
    tagp.set_defaults(func=tag)

    # renamep = subp.add_parser('rename', help='rename files')
    # renamep.add_argument('')

    renump = subp.add_parser('renum', help='renumber tracks')
    renump.add_argument('dir', help='directory containing flac files')
    renump.set_defaults(func=renum)

    clonep = subp.add_parser('clone', help='copy this path to another path')
    clonep.add_argument('dest', help='destination path')
    clonep.add_argument('path', help='paths to clone')
    clonep.set_defaults(func=clone)

    updartp = subp.add_parser('updart', help='update the '
                                             'embedded art in flac files')
    updartp.add_argument('path', help='path containing FLAC files', nargs='+')
    updartp.add_argument('-d', '--depth', help='dir max depth '
                                               '(negative -> unlimited)',
                         type=int, default=-1)
    updartp.add_argument('-f', '--filename', help='file to use (found in '
                                                  'same dir as flac files)',
                         type=str);
    updartp.set_defaults(func=updart)

    no_art_parser = subp.add_parser('noart', help='find albums that have '
                                                  'no artwork file')
    no_art_parser.add_argument('root', help='root folder to begin searching')
    no_art_parser.set_defaults(func=noart)

    transcode_parser = subp.add_parser(
        'transcode', help='transcode the audio to another format')
    transcode_parser.add_argument('-f', '--format', help='output format',
                                  default='mp3', choices=['mp3', 'ogg'])
    transcode_parser.add_argument('-l', '--lstrip',
                                  help="dirs to strip from left of source "
                                       "files when storing. "
                                       "Example: /foo/bar/baz.flac -> "
                                       "/dest/bar/baz.mp3 when -l is 1",
                                  type=int)

    transcode_parser.add_argument('dest', help='destination path')
    transcode_parser.add_argument('path', help='source paths', nargs='+')
    transcode_parser.set_defaults(func=transcode)

    parsedargs = p.parse_args(sys.argv[1:])

    if hasattr(parsedargs, 'func'):
        parsedargs.func(parsedargs)
    else:
        p.print_usage()
        p.exit(status=1, message='Must call a subcommand')
