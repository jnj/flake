import logging
import os
import subprocess
import sys


class Logger:
    def __init__(self, quiet):
        self._quiet = quiet

    def info(self, s):
        if self._quiet:
            return
        logging.info(s)


class CmdInvoker:
    def __init__(self, logger):
        self._logger = logger

    def call(self, tup):
        self._logger.inf(str(tup))
        return subprocess.check_output(tup)


class EchoCmdInvoker:
    def __init__(self, logger):
        self._logger = logger

    def call(self, tup):
        self._logger.info(str(tup))
        return 0


def mkinvoker(args):
    quiet = not args.verbose
    logger = Logger(quiet)
    if args.dry:
        return EchoCmdInvoker(logger)
    return CmdInvoker(logger)


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
