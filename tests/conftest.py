from __future__ import annotations

from pathlib import Path

import piexif
import pytest
from PIL import Image


@pytest.fixture
def make_jpeg(tmp_path: Path):
    """Create a JPEG with the given IFD0 / Exif sub-IFD tags."""

    def _make(name: str = 'photo.jpg', ifd0: dict | None = None, exif: dict | None = None,
              folder: Path | None = None) -> Path:
        path = (folder or tmp_path) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        data = piexif.dump({'0th': ifd0 or {}, 'Exif': exif or {}})
        Image.new('RGB', (4, 4)).save(path, exif=data)
        return path

    return _make
