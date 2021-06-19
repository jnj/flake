from .util import mkinvoker, flac_file_list

import os


def clone(args):
    invoker = mkinvoker(args, concurrent=False)
    srcpath = args.path
    srcdir = srcpath
    dest = args.dest
    if os.path.isdir(dest):
        if dest[-1] != '/':
            dest += '/'
    if os.path.isfile(srcpath) and srcpath[-5:] == '.flac':
        srcdir = os.path.dirname(srcdir)
    cmd = ['rsync', '-av', '--delete', srcdir, dest]
    print(' '.join(cmd))
    pass