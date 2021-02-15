import argparse
import itertools
import logging
import os
import subprocess
import sys

ART_NAMES = [f'{base}.{ext}'
             for ext in ['jpg', 'jpeg', 'png']
             for base in ['cover', 'folder']]


class Logger:
    def __init__(self, quiet):
        self._quiet = quiet

    def info(self, s):
        if self._quiet:
            return
        logging.info(s)


class CmdInvoker:
    def __init__(self, quiet):
        self._quiet = quiet

    def call(self, tup):
        return subprocess.check_output(tup)

    def is_quiet(self):
        return self._quiet


class EchoCmdInvoker:
    def __init__(self, quiet):
        self._quiet = quiet

    def call(self, tup):
        if not self._quiet:
            logging.info('command to invoke: "%s"' % str(tup))
        return 0

    def is_quiet(self):
        return self._quiet


def findflacs(root, maxdepth=-1):
    ext = '.flac'
    extlen = len(ext)

    def is_flac(p):
        return p[-extlen:].lower() == ext

    for f in findfiles(root, maxdepth, 1, is_flac):
        yield f


def findfiles(root, maxdepth=-1, current_depth=1, predicate=lambda f: True):
    if 0 <= maxdepth < current_depth:
        return
    for f in os.listdir(root):
        fullpath = os.path.join(root, f)
        if os.path.isdir(fullpath):
            newdepth = current_depth + 1
            for j in findfiles(fullpath, maxdepth, newdepth, predicate):
                yield j
        elif os.path.isfile(fullpath) and predicate(fullpath):
            yield fullpath


def clone(args):
    pass


def folder_art(filepath):
    for name in ART_NAMES:
        f = os.path.join(os.path.dirname(filepath), name)
        if os.path.exists(f):
            return f
    return None


def clear_art(filepath, cmd_invoker):
    cmdline = ('metaflac', '--remove', '--block-type=PICTURE', filepath)
    return cmd_invoker.call(cmdline)


def set_art(filepath, artpath, cmd_invoker):
    def spec():
        typ = 3
        mime = 'image/jpeg'
        descr = ''
        dims = ''  # leave to reader to determine from file
        return '%s|%s|%s|%s|%s' % (typ, mime, descr, dims, artpath)

    img_option = '--import-picture-from=%s' % spec()
    metaflac_cmdline = ('metaflac', img_option, filepath)
    if not cmd_invoker.is_quiet():
        logging.info("%s %s %s" % metaflac_cmdline)
    retcode = cmd_invoker.call(metaflac_cmdline)
    return retcode


def mkinvoker(args):
    quiet = not args.verbose
    if args.dry:
        return EchoCmdInvoker(quiet)
    return CmdInvoker(quiet)


def updart(args):
    gens = [findflacs(path, args.depth) for path in args.path]
    files = list(itertools.chain(*gens))
    if files:
        invoker = mkinvoker(args)
        for file in files:
            cover = folder_art(file)
            if cover:
                clear_art(file, invoker)
                set_art(file, cover, invoker)


def config_logging():
    formatstring = '%(asctime)s|%(module)s|%(levelname)s|%(message)s'
    formatter = logging.Formatter(formatstring)
    logging.basicConfig(level=logging.INFO, format=formatstring)
    stdouthandler = logging.StreamHandler(sys.stdout)
    stdouthandler.setLevel(logging.INFO)
    stdouthandler.setFormatter(formatter)
    rootlogger = logging.getLogger()
    for h in rootlogger.handlers:
        rootlogger.removeHandler(h)
    rootlogger.addHandler(stdouthandler)


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
    parsedargs.func(parsedargs)
