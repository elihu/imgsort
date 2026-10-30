from __future__ import annotations

import os
import re
import shutil
from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path

IMAGE_EXTENSIONS = frozenset({'.jpg', '.jpeg', '.png', '.tiff'})
VIDEO_EXTENSIONS = frozenset({'.avi', '.mp4', '.mpg', '.wmv', '.mov'})

MIN_YEAR = 1900

# Compiled once at import time
_WHATSAPP   = re.compile(r'IMG[-_](\d{4})(\d{2})(\d{2})[-_](?:WA)?(\d{2})(\d{2})')
_SCREENSHOT = re.compile(r'Screenshot_(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})')
_GPHOTOS    = re.compile(r'(20\d{2})(\d{2})(\d{2})-0*(\d{2})(\d{2})')

_PATTERNS = (
    (_WHATSAPP, 'WA'),
    (_SCREENSHOT, 'Screenshot'),
    (_GPHOTOS, 'GPhotos'),
)


def is_plausible(dt: datetime) -> bool:
    """Reject dates that are obviously bogus (zeroed, epoch defaults, future)."""
    return dt.year >= MIN_YEAR and dt <= datetime.now() + timedelta(days=1)


def date_info(dt: datetime, suffix: str = '') -> dict:
    """Build the year/month/stem dict used to place a file."""
    stem = dt.strftime('%Y_%m_%d-%H_%M_%S')
    if suffix:
        stem = f'{stem}-{suffix}'
    return {'year': f'{dt.year:04d}', 'month': f'{dt.month:02d}', 'stem': stem}


def date_from_filename(filename: str) -> dict | None:
    """Extract date info from WhatsApp, Screenshot, or Google Photos filename patterns."""
    for pattern, label in _PATTERNS:
        m = pattern.search(filename)
        if not m:
            continue
        year, month, day, hh, mm = m.groups()
        # Only the date part is validated: in WhatsApp names the last 4 digits
        # are a sequence number (WA0012), not a time.
        try:
            dt = datetime(int(year), int(month), int(day))
        except ValueError:
            continue
        if not is_plausible(dt):
            continue
        stem = f'{year}_{month}_{day}-{hh}_{mm}-{label}'
        if label == 'Screenshot':
            return {'year': 'Screenshots', 'month': None, 'stem': stem}
        return {'year': year, 'month': month, 'stem': stem}

    return None


def date_from_mtime(path: str | Path, suffix: str = '') -> dict:
    """Fallback: build date info from the file's modification time."""
    return date_info(datetime.fromtimestamp(os.path.getmtime(path)), suffix)


def dest_folder(base: str | Path, year: str, month: str | None) -> str:
    """Build the destination folder path from year and optional month."""
    if year and month:
        return os.path.join(base, year, month)
    if year:
        return os.path.join(base, year)
    return os.path.join(base, 'Unknown')


def walk_files(
    source_dir: str | Path, dest_dir: str | Path, extensions: frozenset[str],
) -> Iterator[str]:
    """
    Yield paths under source_dir whose extension is in extensions.

    dest_dir is pruned from the walk so that sorting into a subfolder of the
    source (the default: ./ → ./sorted/...) never re-copies already sorted files.
    """
    dest = Path(dest_dir).resolve()
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if Path(root, d).resolve() != dest]
        for file in sorted(files):
            if Path(file).suffix.lower() in extensions:
                yield os.path.join(root, file)


def safe_copy(src: str, folder: str, stem: str, ext: str) -> str:
    """Copy src to folder/stem+ext, appending _N on filename collision."""
    os.makedirs(folder, exist_ok=True)
    dest = os.path.join(folder, f'{stem}{ext}')
    n = 1
    while os.path.exists(dest):
        dest = os.path.join(folder, f'{stem}_{n}{ext}')
        n += 1
    shutil.copy2(src, dest)
    return dest
