from __future__ import annotations

import os
import re
import shutil
from datetime import datetime

IMAGE_EXTENSIONS = frozenset({'.jpg', '.jpeg', '.png', '.tiff'})
VIDEO_EXTENSIONS = frozenset({'.avi', '.mp4', '.mpg', '.wmv', '.mov'})

# Compiled once at import time
_WHATSAPP   = re.compile(r'IMG[-_](\d{4})(\d{2})(\d{2})[-_](?:WA)?(\d{2})(\d{2})')
_SCREENSHOT = re.compile(r'Screenshot_(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})')
_GPHOTOS    = re.compile(r'(20\d{2})(\d{2})(\d{2})-0*(\d{2})(\d{2})')


def date_from_filename(filename: str) -> dict | None:
    """Extract date info from WhatsApp, Screenshot, or Google Photos filename patterns."""
    m = _WHATSAPP.search(filename)
    if m:
        return {
            'year': m.group(1),
            'month': m.group(2),
            'stem': f'{m.group(1)}_{m.group(2)}_{m.group(3)}-{m.group(4)}_{m.group(5)}-WA',
        }

    m = _SCREENSHOT.search(filename)
    if m:
        return {
            'year': 'Screenshots',
            'month': None,
            'stem': f'{m.group(1)}_{m.group(2)}_{m.group(3)}-{m.group(4)}_{m.group(5)}-Screenshot',
        }

    m = _GPHOTOS.search(filename)
    if m:
        return {
            'year': m.group(1),
            'month': m.group(2),
            'stem': f'{m.group(1)}_{m.group(2)}_{m.group(3)}-{m.group(4)}_{m.group(5)}-GPhotos',
        }

    return None


def date_from_mtime(path: str, suffix: str = '') -> dict:
    """Fallback: build date info from the file's modification time."""
    dt = datetime.fromtimestamp(os.path.getmtime(path))
    stem = str(dt).replace('-', '_').replace(':', '_').replace(' ', '-')
    if suffix:
        stem = f'{stem}-{suffix}'
    return {
        'year': str(dt.year),
        'month': f'{dt.month:02d}',
        'stem': stem,
    }


def dest_folder(base: str, year: str, month: str | None) -> str:
    """Build the destination folder path from year and optional month."""
    if year and month:
        return os.path.join(base, year, month)
    if year:
        return os.path.join(base, year)
    return os.path.join(base, 'Unknown')


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
