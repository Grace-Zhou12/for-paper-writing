# for-paper-writing

## Photo File Tagger & Organizer

A Python tool for photographers to tag files and automatically organize them into corresponding folders.

### Supported Formats

| Category | Extensions |
|----------|-----------|
| Images   | jpg, jpeg, png, bmp, gif, tiff, tif, webp, heic, heif |
| RAW      | cr2, cr3, nef, arw, orf, rw2, dng, raf, pef, srw |
| Video    | mp4, mov, avi, mkv, wmv |
| Other    | psd, ai, svg, pdf |

### Usage

```bash
# Launch GUI (default)
python photo_tagger.py

# Launch CLI mode
python photo_tagger.py --cli
```

### Running Tests

```bash
python -m unittest test_photo_tagger -v
```