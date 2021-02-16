import itertools
import os

from .util import mkinvoker, flac_file_list

ART_NAMES = [f'{base}.{ext}'
             for ext in ['jpg', 'jpeg', 'png']
             for base in ['cover', 'folder']]


def folder_art(filepath):
    for name in ART_NAMES:
        f = os.path.join(os.path.dirname(filepath), name)
        if os.path.exists(f):
            return f
    return None


def clear_art(filepath):
    cmdline = ('metaflac', '--remove', '--block-type=PICTURE', filepath)
    return cmdline


def set_art(filepath, artpath, cmd_invoker):
    cmds = [clear_art(filepath)]

    def spec():
        typ = 3
        mime = 'image/jpeg'
        descr = ''
        dims = ''  # leave to reader to determine from file
        return f'{typ}|{mime}|{descr}|{dims}|{artpath}'

    img_option = f'--import-picture-from={spec()}'
    metaflac_cmdline = ('metaflac', img_option, filepath)
    cmds.append(metaflac_cmdline)
    return cmd_invoker.call(cmds)


def updart(args):
    files = flac_file_list(args.path, args.depth)
    if files:
        invoker = mkinvoker(args)
        for file in files:
            cover = folder_art(file)
            if cover:
                set_art(file, cover, invoker)
        invoker.wait()
