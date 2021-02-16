import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from .util import CmdInvoker, Logger, flac_file_list


class OggEncodeCommand:
    def __init__(self, sourcefile, destfile, invoker, logger):
        self._src = sourcefile
        self._dst = destfile
        self._invoker = invoker
        self._logger = logger

    def __call__(self, *args, **kwargs):
        self.run()

    def run(self):
        cmd = ['oggenc', '-Q', '-q', '8', '-o', self._dst, self._src]
        self._invoker.call([cmd])


class Mp3EncodeCommand:
    def __init__(self, sourcefile, destfile, invoker, logger):
        self._src = sourcefile
        self._dst = destfile
        self._invoker = invoker
        self._logger = logger

    def __call__(self, *args, **kwargs):
        self.run()

    def run(self):
        get_tags_cmd = ('metaflac', '--export-tags-to=-', self._src)
        outputs = self._invoker.call([get_tags_cmd])
        tag_re = re.compile('([A-Z]+)=(.+)')
        tagslist = outputs[0].splitlines()
        tagsdict = {}

        for t in tagslist:
            t = t.decode()
            match = tag_re.match(t)
            if match:
                tagsdict[match.group(1)] = match.group(2)

        tagsopts = {
            'ARTIST': 'ta',
            'ALBUM': 'tl',
            'GENRE': 'tg',
            'DATE': 'ty',
            'TITLE': 'tt',
            'TRACKNUMBER': 'tn'
        }

        tag_options = []
        for flactag, lameopt in tagsopts.items():
            if flactag in tagsdict:
                tag_options.append(f'--{lameopt}')
                tag_options.append(tagsdict[flactag])

        deflac = ('flac', '--silent', '-d', '-c', self._src)
        lamenc = ['lame', '-V', '3'] + tag_options + \
                 ['--silent', '-', self._dst]
        self._logger.info(deflac)
        self._logger.info(lamenc)
        cmd1 = subprocess.run(deflac, check=True, capture_output=True)
        cmd2 = subprocess.run(lamenc, input=cmd1.stdout, capture_output=True)
        cmd1.check_returncode()
        cmd2.check_returncode()


def get_dest_file_path(root, srcfile, extension, lstrip):
    parts = os.path.dirname(srcfile).split(os.path.sep)
    prefix = [p for p in parts if p][lstrip:]
    destdir = os.path.join(root, os.path.join(*prefix))
    base, _ = os.path.splitext(os.path.basename(srcfile))
    newfile = f'{base}.{extension}'
    fullpath = os.path.join(destdir, newfile)
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    return fullpath


def encoder(fmt, invoker, logger, srcfile, destfile):
    if fmt == 'mp3':
        return Mp3EncodeCommand(srcfile, destfile, invoker, logger)
    else:
        return OggEncodeCommand(srcfile, destfile, invoker, logger)


def transcode(args):
    logger = Logger(not args.verbose)
    files = flac_file_list(args.path)
    with ThreadPoolExecutor() as pool:
        futures = []

        for src in files:
            destfile = get_dest_file_path(
                args.dest,
                src,
                args.format,
                args.lstrip
            )
            if args.dry:
                logger.info(f'{src} -> {destfile}')
                continue
            invoker = CmdInvoker(logger)
            enc = encoder(args.format, invoker, logger, src, destfile)
            futures.append(pool.submit(enc))

        for f in futures:
            f.result()
