from .util import mkinvoker, flac_file_list


def renum(args):
    flacfiles = flac_file_list(args.dir, maxdepth=1)
    invoker = mkinvoker(args, concurrent=False)
    tracks = {}
    min_no = 999999
    for f in flacfiles:
        cmd = ['metaflac', '--show-tag=TRACKNUMBER', f]
        invoker.call([cmd])
        output = invoker.wait()
        _, trackno = output[0].decode('utf-8').strip().split('=')
        n = int(trackno)
        tracks[n] = f
        min_no = min(min_no, n)
    i = 1
    j = min_no
    while tracks:
        if j in tracks:
            new_track_no = f'{i:02}'
            f = tracks[j]
            cmd = ['metaflac', f'--remove-tag=TRACKNUMBER', f]
            invoker.call([cmd])
            cmd = ['metaflac', f'--set-tag=TRACKNUMBER={new_track_no}', f]
            invoker.call([cmd])
            invoker.wait()
            del tracks[j]
            i += 1
        j += 1


