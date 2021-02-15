import itertools
import os

from .util import mkinvoker, findflacs

ART_NAMES = [f'{base}.{ext}'
             for ext in ['jpg', 'jpeg', 'png']
             for base in ['cover', 'folder']]


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
        return f'{typ}|{mime}|{descr}|{dims}|{artpath}'

    img_option = f'--import-picture-from={spec()}'
    metaflac_cmdline = ('metaflac', img_option, filepath)
    retcode = cmd_invoker.call(metaflac_cmdline)
    return retcode


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
