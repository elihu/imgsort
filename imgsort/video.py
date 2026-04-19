from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from rich import print

from .utils import VIDEO_EXTENSIONS, date_from_mtime, dest_folder, safe_copy

logging.getLogger('hachoir').setLevel(logging.ERROR)

_EPOCH_YEAR = 1904  # Default timestamp in some MP4/MOV files — treat as missing


def _date_from_metadata(path: str) -> dict | None:
    """Extract creation date from video metadata via hachoir. Returns None on any failure."""
    if os.path.getsize(path) == 0:
        print(f'[yellow]Skipping empty file:[/yellow] {path}')
        return None

    parser = createParser(path)
    if not parser:
        print(f'[yellow]Cannot parse:[/yellow] {path}')
        return None

    with parser:
        try:
            metadata = extractMetadata(parser)
        except Exception as err:
            print(f'[yellow]Metadata error in[/yellow] {path}: {err}')
            return None

    if not metadata:
        return None

    for line in metadata.exportPlaintext():
        if line.split(':')[0].lower() != '- creation date':
            continue
        try:
            dt = datetime.strptime(line.split('date: ')[1], '%Y-%m-%d %H:%M:%S')
        except (ValueError, IndexError):
            return None
        if dt.year == _EPOCH_YEAR:
            return None
        stem = str(dt).replace('-', '_').replace(':', '_').replace(' ', '-')
        return {'year': str(dt.year), 'month': f'{dt.month:02d}', 'stem': stem}

    return None


def organize_videos(source_dir: str, dest_dir: str) -> None:
    """
    Recursively copy videos from source_dir into year/month subfolders under dest_dir.

    Date resolution order:
      1. Embedded metadata (via hachoir)
      2. File modification time
    """
    for root, _, files in os.walk(source_dir):
        for file in files:
            ext = Path(file).suffix.lower()
            if ext not in VIDEO_EXTENSIONS:
                continue
            path = os.path.join(root, file)
            info = _date_from_metadata(path) or date_from_mtime(path)
            folder = dest_folder(dest_dir, info['year'], info.get('month'))
            dest   = safe_copy(path, folder, info['stem'], ext)
            print(f'[green]Copied:[/green] {path} → {dest}')
