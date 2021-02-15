import argparse
import logging
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


def mkargparser():
    desc = """
    Flake: a tool for managing a local music collection.
    """
    p = argparse.ArgumentParser(
        prog='flake',
        description=desc,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    commands = sorted(['updart', 'clone'])
    p.add_argument('-v', '--verbose',
                   help='log details to stdout',
                   action='store_true')
    p.add_argument('command', help='Command to invoke', choices=commands)

    return p


def main(args):
    argparser = mkargparser()
    argparser.parse_args(args)


if __name__ == '__main__':
    main(sys.argv[1:])
