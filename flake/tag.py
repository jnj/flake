from .util import mkinvoker


def show_tag_command(files):
    cmd = ['metaflac', '--export-tags-to=-']
    cmd.extend(files)
    return cmd


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


def only_display(args, tags):
    if args.show:
        return True
    if not any(getattr(args, argname) is not None for (argname, _) in tags):
        return True
    return False


def tag(args):
    invoker = mkinvoker(args, concurrent=False)
    tags = [['artist', 'ARTIST'],
            ['aartist', 'ALBUMARTIST'],
            ['date', 'DATE'],
            ['genre', 'GENRE'],
            ['discno', 'DISCNUMBER'],
            ['trackno', 'TRACKNUMBER'],
            ['title', 'TITLE']]

    if only_display(args, tags):
        show_tags(invoker, args.file)
    else:
        for argname, tagname in tags:
            set_tag(args, argname, tagname, invoker)
