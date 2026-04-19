from __future__ import annotations

import os
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS
from rich import print

from .utils import IMAGE_EXTENSIONS, date_from_filename, date_from_mtime, dest_folder, safe_copy


def _extract_exif(path: str) -> dict:
    try:
        with Image.open(path) as img:
            return {TAGS.get(tag, tag): val for tag, val in img.getexif().items()}
    except Exception:
        return {}


def _date_from_exif(exif: dict, camera: str) -> dict | None:
    """Parse date info from EXIF tags. Returns None if no date is found."""
    date_str = exif.get('DateTimeOriginal') or exif.get('DateTime')
    if not date_str:
        return None
    # EXIF format: "YYYY:MM:DD HH:MM:SS"
    stem = date_str.replace(':', '_').replace(' ', '-')
    return {
        'year': date_str[:4],
        'month': date_str[5:7],
        'stem': f'{stem}-{camera}',
    }


def organize_images(source_dir: str, dest_dir: str) -> None:
    """
    Recursively copy images from source_dir into year/month subfolders under dest_dir.

    Date resolution order:
      1. EXIF metadata (DateTimeOriginal or DateTime)
      2. Filename pattern  (WhatsApp, Screenshot, Google Photos)
      3. File modification time
    """
    for root, _, files in os.walk(source_dir):
        for file in files:
            ext = Path(file).suffix.lower()
            if ext not in IMAGE_EXTENSIONS:
                continue
            path = os.path.join(root, file)
            exif   = _extract_exif(path)
            camera = exif.get('Model', 'Unknown-Camera').replace(' ', '').replace('\0', '')
            info   = (
                _date_from_exif(exif, camera)
                or date_from_filename(file)
                or date_from_mtime(path, suffix=camera)
            )
            folder = dest_folder(dest_dir, info['year'], info.get('month'))
            dest   = safe_copy(path, folder, info['stem'], ext)
            print(f'[green]Copied:[/green] {path} → {dest}')
