# flake
Tools for managing a local FLAC library

Some operations that are supported:
* Update the embedded artwork
* Clone to another device
* Transcode from FLAC to MP3 or OGG
* Set tags
## Requirements
* `python3`
* `metaflac` for setting album art and tags
* `rsync` for cloning
* `lame`, `flac`, and `oggenc` for transcoding

## Example usage

### Update the artwork
If your album is in `/media/music/Aerosmith/Rocks` and you just added/updated 
the cover artwork at `/media/music/Aerosmith/Rocks/cover.jpg`, then run this
to embed it into the flac files:

`python3 flake/main.py updart /media/music/Aerosmith/Rocks`

### Transcode to MP3
`python flake/main.py transcode -l 2 /media/mp3s /media/music/Aerosmith/Rocks`

This will result in mp3 files (mp3 is the default) for your songs, and they 
will be in the folder `/media/mp3s/Aerosmith/Rocks`. The reason for this is 
that the `-l 2` option tells flake to strip away two path components from the 
left of the source file path when determining the output file path, so the 
`/media/music` prefix is discarded from the output paths before they are
copied under the destination root `/media/mp3s`.

