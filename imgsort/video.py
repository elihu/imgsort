from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from rich import print

from .utils import (
    VIDEO_EXTENSIONS,
    date_from_mtime,
    date_info,
    dest_folder,
    is_plausible,
    safe_copy,
    walk_files,
)

logging.getLogger('hachoir').setLevel(logging.ERROR)

_EPOCH_YEAR = 1904  # Default timestamp in some MP4/MOV files — treat as missing
# Containers whose creation date is stored in UTC (MP4/MOV mvhd, ASF file properties)
_UTC_CONTAINERS = frozenset({'.mp4', '.mov', '.wmv'})


def _date_from_metadata(path: str) -> dict | None:
    """Extract creation date from video metadata via hachoir. Returns None on any failure."""
    if os.path.getsize(path) == 0:
        print(f'[yellow]Skipping empty file:[/yellow] {path}')
        return None

    try:
        parser = createParser(path)
        if not parser:
            print(f'[yellow]Cannot parse:[/yellow] {path}')
            return None
        with parser:
            metadata = extractMetadata(parser)
    except Exception as err:
        print(f'[yellow]Metadata error in[/yellow] {path}: {err}')
        return None

    dt = metadata.get('creation_date', None) if metadata else None
    if not isinstance(dt, datetime) or dt.year == _EPOCH_YEAR:
        return None
    if Path(path).suffix.lower() in _UTC_CONTAINERS:
        dt = dt.replace(tzinfo=UTC).astimezone().replace(tzinfo=None)
    if not is_plausible(dt):
        return None
    return date_info(dt)


def organize_videos(source_dir: str | Path, dest_dir: str | Path) -> None:
    """
    Recursively copy videos from source_dir into year/month subfolders under dest_dir.

    Date resolution order:
      1. Embedded metadata (via hachoir)
      2. File modification time
    """
    copied = failed = 0
    for path in walk_files(source_dir, dest_dir, VIDEO_EXTENSIONS):
        try:
            info   = _date_from_metadata(path) or date_from_mtime(path)
            folder = dest_folder(dest_dir, info['year'], info.get('month'))
            dest   = safe_copy(path, folder, info['stem'], Path(path).suffix.lower())
        except OSError as err:
            print(f'[red]Error:[/red] {path}: {err}')
            failed += 1
            continue
        print(f'[green]Copied:[/green] {path} → {dest}')
        copied += 1
    print(f'[bold]Done:[/bold] {copied} copied, {failed} failed')
