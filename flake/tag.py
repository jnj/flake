import glob
import os.path
import shutil

from .util import mkinvoker
from mutagen.flac import FLAC

LCASE_WORDS = {' The ', ' Of ', ' In ', ' A '}


def show_tag_command(files):
    cmd = ['metaflac', '--export-tags-to=-']
    cmd.extend(files)
    return cmd


def clear_tag_command(tagname, files):
    cmd = ['metaflac', f'--remove-tag={tagname}']
    cmd.extend(files)
    return cmd


def remove_all_tags(args, invoker):
    if args.removeall:
        cmd = ['metaflac', '--remove-all-tags']
        cmd.extend(args.file)
        invoker.call([cmd])


def add_tag_command(tagname, value, files):
    cmd = ['metaflac', f'--set-tag={tagname}={value}']
    cmd.extend(files)
    return cmd


def set_tag(args, argname, tagname, invoker):
    if hasattr(args, argname):
        argval = getattr(args, argname)
        if argval is not None:
            clear = clear_tag_command(tagname, args.file)
            invoker.call([clear])
            if not args.remove:
                settag = add_tag_command(tagname, argval, args.file)
                invoker.call([settag])


def show_tags(invoker, files):
    output = invoker.call([show_tag_command(files)])
    if isinstance(output, list):
        for e in output:
            d = e.decode().split('\n')
            for part in d:
                print(part)


def get_tags(invoker, file):
    output = invoker.call([show_tag_command([files])])


def only_display(args, tags):
    if args.show:
        return True
    if not any(getattr(args, argname) is not None for (argname, _) in tags):
        return True
    return False


def clean_tags(invoker, files):
    for file in files:
        if os.path.isdir(file):
            clean_dir(file)


def clean_dir(dirpath):
    flacs = glob.glob(os.path.join(dirpath, '*.flac'))
    audio_by_file = {}
    all_artists = set()
    all_discs = set()
    disctag = 'DISCNUMBER'
    aatag = 'ALBUMARTIST'

    def tagval(au, tag):
        x = au.get(tag.lower())
        if x is None:
            return x
        return x[0]

    for flacfile in flacs:
        audio = FLAC(flacfile)
        audio_by_file[flacfile] = audio

    required_tags = {'ALBUM', 'ARTIST', 'TRACKNUMBER', 'TITLE'}
    for flacfile, audio in audio_by_file.items():
        if not all(t.lower() in audio.keys() for t in required_tags):
            print(f'File {flacfile} is missing tags. Aborting. (Keys={audio.keys()})')
            return

    for flacfile, audio in audio_by_file.items():
        for tagname in ['ARTIST', 'ALBUM', 'TITLE']:
            print(f'file is {flacfile}')
            print(f'cleaning tag {tagname}, value={tagval(audio, tagname)}')
            audio[tagname] = lcase_clean(tagval(audio, tagname), LCASE_WORDS)
            print(f'Now tag value is {audio[tagname]}')

    for flacfile, audio in audio_by_file.items():
        all_artists.add(tagval(audio, 'ARTIST'))
        if disctag in audio.keys():
            all_discs.add(tagval(audio, disctag))

    comp = len(all_artists) > 1

    # set albumartist to 'Various Artists' if compilation.
    # otherwise, remove it.
    for audio in audio_by_file.values():
        if aatag in audio.keys():
            del audio[aatag]
        if comp:
            audio[aatag] = 'Various Artists'

    # remove discnumber tag if not multidisc.
    multidisc = len(all_discs) > 1
    for audio in audio_by_file.values():
        if not multidisc and disctag in audio.keys():
            del audio[disctag]

    # remove unwanted tags
    allowed_tags = {
        'ALBUM', 'ALBUMARTIST', 'DATE', 'GENRE', 'TITLE',
        'TRACKNUMBER', 'DISCNUMBER'
    }

    for audio in audio_by_file.values():
        for t in audio.keys():
            if t.upper() not in allowed_tags:
                del audio[t]
            else:
                audio[t.upper()] = audio[t]

    # save before renaming.
    for audio in audio_by_file.values():
        audio.save(deleteid3=True)

    for flacfile, _ in audio_by_file.items():
        audio = FLAC(flacfile)
        filebase = os.path.basename(flacfile)
        filedir = os.path.dirname(flacfile)
        trackno = tagval(audio, 'TRACKNUMBER')
        title = tagval(audio, 'TITLE')
        if trackno is None or title is None:
            print(f'Aborting. Something is wrong. Tags={audio.tags}')
            return
        new_file_name = fs_sanitize(f'{trackno}-{title}.flac')

        if multidisc:
            discnum = tagval(audio, disctag)
            new_file_name = fs_sanitize(f'{discnum}-{trackno}-{title}.flac')

        fullpath = os.path.join(filedir, new_file_name)
        print(f"Renaming: {flacfile} -> {fullpath}")
        shutil.move(flacfile, fullpath)


def fs_sanitize(name):
    bad_chars = ["'", ';', '!', '*', '/', '\\']
    for c in bad_chars:
        name = name.replace(c, '-')
    return name


def lcase_clean(text, to_lcase):
    for s in to_lcase:
        if s in text:
            text = text.replace(s, s.lower())
    return text


def tag(args):
    invoker = mkinvoker(args, concurrent=False)
    tags = [['artist', 'ARTIST'],
            ['aartist', 'ALBUMARTIST'],
            ['date', 'DATE'],
            ['genre', 'GENRE'],
            ['discno', 'DISCNUMBER'],
            ['trackno', 'TRACKNUMBER'],
            ['title', 'TITLE'],
            ['album', 'ALBUM']]

    if args.clean:
        clean_tags(invoker, args.file)
    elif only_display(args, tags):
        show_tags(invoker, args.file)
    else:
        remove_all_tags(args, invoker)
        for argname, tagname in tags:
            set_tag(args, argname, tagname, invoker)
