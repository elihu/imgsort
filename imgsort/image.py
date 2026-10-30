from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from PIL import Image
from PIL.ExifTags import IFD, TAGS
from rich import print

from .utils import (
    IMAGE_EXTENSIONS,
    date_from_filename,
    date_from_mtime,
    date_info,
    dest_folder,
    is_plausible,
    safe_copy,
    walk_files,
)

# Most specific first: capture time, then digitization, then last modification
_DATE_TAGS = ('DateTimeOriginal', 'DateTimeDigitized', 'DateTime')
_UNSAFE_CHARS = re.compile(r'[^A-Za-z0-9_-]')


def _extract_exif(path: str) -> dict:
    """Read IFD0 plus the Exif sub-IFD, where DateTimeOriginal actually lives."""
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            tags = dict(exif.items())
            tags.update(exif.get_ifd(IFD.Exif))
    except Exception:
        return {}
    return {TAGS.get(tag, tag): val for tag, val in tags.items()}


def _camera_name(exif: dict) -> str:
    """Camera model sanitized for use in a filename (no spaces, slashes, NULs...)."""
    model = _UNSAFE_CHARS.sub('', str(exif.get('Model') or ''))
    return model or 'Unknown-Camera'


def _date_from_exif(exif: dict, camera: str) -> dict | None:
    """Parse date info from EXIF tags. Returns None if no valid date is found."""
    for tag in _DATE_TAGS:
        raw = exif.get(tag)
        if not raw:
            continue
        # EXIF format: "YYYY:MM:DD HH:MM:SS", sometimes NUL-padded
        try:
            dt = datetime.strptime(str(raw).strip('\0 '), '%Y:%m:%d %H:%M:%S')
        except ValueError:
            continue
        if is_plausible(dt):
            return date_info(dt, camera)
    return None


def organize_images(source_dir: str | Path, dest_dir: str | Path) -> None:
    """
    Recursively copy images from source_dir into year/month subfolders under dest_dir.

    Date resolution order:
      1. EXIF metadata (DateTimeOriginal, DateTimeDigitized or DateTime)
      2. Filename pattern  (WhatsApp, Screenshot, Google Photos)
      3. File modification time
    """
    copied = failed = 0
    for path in walk_files(source_dir, dest_dir, IMAGE_EXTENSIONS):
        try:
            exif   = _extract_exif(path)
            camera = _camera_name(exif)
            info   = (
                _date_from_exif(exif, camera)
                or date_from_filename(Path(path).name)
                or date_from_mtime(path, suffix=camera)
            )
            folder = dest_folder(dest_dir, info['year'], info.get('month'))
            dest   = safe_copy(path, folder, info['stem'], Path(path).suffix.lower())
        except OSError as err:
            print(f'[red]Error:[/red] {path}: {err}')
            failed += 1
            continue
        print(f'[green]Copied:[/green] {path} → {dest}')
        copied += 1
    print(f'[bold]Done:[/bold] {copied} copied, {failed} failed')
