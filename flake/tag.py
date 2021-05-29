from .util import mkinvoker


def clear_tag_command(tagname, files):
    cmd = ['metaflac', f'--remove-tag={tagname}']
    cmd.extend(files)
    return cmd


def add_tag_command(tagname, value, files):
    cmd = ['metaflac', f'--set-tag={tagname}={value}']
    cmd.extend(files)
    return cmd


def set_tag(args, argname, tagname, invoker):
    if hasattr(args, argname):
        argval = getattr(args, argname)
        if argval is not None:
            clear = (clear_tag_command(tagname, args.file))
            invoker.call([clear])
            settag = add_tag_command(tagname, argval, args.file)
            invoker.call([settag])


def tag(args):
    invoker = mkinvoker(args, concurrent=False)
    tags = [['artist', 'ARTIST'],
            ['aartist', 'ALBUMARTIST'],
            ['date', 'DATE'],
            ['genre', 'GENRE']]
    for argname, tagname in tags:
        set_tag(args, argname, tagname, invoker)
