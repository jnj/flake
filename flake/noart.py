import os
from .util import flac_file_list, Logger
from .updart import ART_NAMES


def has_art(directory):
    for n in ART_NAMES:
        if os.path.exists(os.path.join(directory, n)):
            return True
    return False


def noart(args):
    files = flac_file_list([args.root])
    dirs = set(os.path.dirname(f) for f in files)
    for d in dirs:
        if not has_art(d):
            print(d)
