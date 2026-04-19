# imgsort

A Python CLI tool that sorts and organizes photo and video galleries into `YEAR/MONTH` subfolders based on embedded metadata.

[![License: Apache-2.0][license-img]][license] [![GitHub Release][release-img]][release]

## Features

- **Images** — reads EXIF date (JPG, JPEG, PNG, TIFF) via Pillow
- **Videos** — reads embedded creation date (MP4, AVI, MOV, WMV, MPG) via Hachoir
- **Smart fallback chain** — EXIF/metadata → filename pattern → file modification time
- **Filename pattern recognition** — WhatsApp, Google Photos, and Screenshot naming conventions
- **Collision-safe** — duplicate filenames get a numeric suffix instead of being overwritten
- **Non-destructive** — always copies, never moves or deletes the originals

## Output structure

```
sorted/
├── image/
│   ├── 2023/
│   │   ├── 01/   ← YYYY/MM from EXIF
│   │   └── 07/
│   └── Screenshots/  ← pattern-detected screenshots
└── video/
    └── 2023/
        └── 08/
```

## Date resolution priority

| Priority | Images | Videos |
|----------|--------|--------|
| 1st | EXIF `DateTimeOriginal` / `DateTime` | Hachoir `creation date` |
| 2nd | Filename pattern (WhatsApp / GPhotos / Screenshot) | — |
| Last | File modification time | File modification time |

### Recognized filename patterns

| Source | Example filename |
|--------|-----------------|
| WhatsApp | `IMG-20240115-WA0012.jpg` |
| WhatsApp (old) | `IMG_20240115_1234.jpg` |
| Google Photos | `20240115-1234.jpg` |
| Screenshot | `Screenshot_2024-01-15-12-34.png` |

## Requirements

- Python 3.10+
- [Poetry](https://python-poetry.org) (for building)

## Installation

Clone the repository and build/install with Make:

```bash
git clone https://github.com/elihu/imgsort.git
cd imgsort
make install
```

For development (editable install):

```bash
make dev
```

To uninstall:

```bash
make uninstall
```

## Usage

```
imgsort [image|video] [SOURCE] [OPTIONS]
```

### Sort images

```bash
# Current directory → ./sorted/image
imgsort image

# Custom source and destination
imgsort image /path/to/photos --dst /path/to/output
```

### Sort videos

```bash
# Current directory → ./sorted/video
imgsort video

# Custom source and destination
imgsort video /path/to/videos --dst /path/to/output
```

### Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--dst` | `-d` | `./sorted/image` or `./sorted/video` | Destination directory |
| `--help` | | | Show help and exit |

### Full help

```bash
imgsort --help
imgsort image --help
imgsort video --help
```

## Tools

`tools/change_time.py` is a standalone utility that stamps sequential EXIF timestamps onto a folder of images (useful for re-dating an unordered batch). Supports JPEG and TIFF; PNG is skipped (piexif limitation).

```bash
python tools/change_time.py
```

Edit the `__main__` block to set the source directory and starting date.

## License

Licensed under the [Apache 2.0 License](LICENSE).

[license]: https://github.com/elihu/imgsort/blob/main/LICENSE
[license-img]: https://img.shields.io/github/license/elihu/imgsort?style=flat&logo=apache
[release]: https://github.com/elihu/imgsort/releases/
[release-img]: https://img.shields.io/github/v/release/elihu/imgsort?logo=github
