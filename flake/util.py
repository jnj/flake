import concurrent.futures as fut
import itertools
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


class PoolInvoker:
    def __init__(self, quiet, dryrun):
        self._exec = fut.ThreadPoolExecutor()
        self._quiet = quiet
        self._dryrun = dryrun
        self._futures = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exec.shutdown(True)

    def wait(self):
        results = []
        for f in self._futures:
            results.append(f.result())
        self._futures.clear()
        return results

    def call(self, commands):
        inv = create_invoker(self._quiet, self._dryrun)

        def task():
            inv.call(commands)

        f = self._exec.submit(task)
        # not safe for concurrent uses of call()
        self._futures.append(f)


class CmdInvoker:
    def __init__(self, logger):
        self._logger = logger
        self._outputs = []

    def wait(self):
        outputs = list(self._outputs)
        self._outputs.clear()
        return outputs

    def call(self, commands):
        for c in commands:
            self._logger.info(str(c))
            self._outputs.append(subprocess.check_output(c))
        # todo check output
        return self._outputs


class EchoCmdInvoker:
    def __init__(self, logger):
        self._logger = logger

    def wait(self):
        pass

    def call(self, commands):
        for c in commands:
            self._logger.info(str(c))
        return []


def mkinvoker(args, concurrent=True):
    quiet = not args.verbose
    dryrun = args.dry

    if concurrent:
        return PoolInvoker(quiet, dryrun)

    return create_invoker(quiet, dryrun)


def create_invoker(quiet, dryrun):
    if dryrun:
        return EchoCmdInvoker(Logger(quiet))
    return CmdInvoker(Logger(quiet))


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


def flac_file_list(paths, maxdepth=-1):
    gens = [findflacs(path, maxdepth) for path in paths]
    return list(itertools.chain(*gens))


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
    try:
        for f in os.listdir(root):
            fullpath = os.path.join(root, f)
            if os.path.isdir(fullpath):
                newdepth = current_depth + 1
                for j in findfiles(fullpath, maxdepth, newdepth, predicate):
                    yield j
            elif os.path.isfile(fullpath) and predicate(fullpath):
                yield fullpath
    except PermissionError:
        pass
