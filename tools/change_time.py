"""
Utility script: stamp sequential EXIF timestamps onto images.

Each file in the source directory receives a timestamp 1 second after
the previous one, starting from date_orig + 1s.

Supported formats: JPEG, TIFF  (PNG is skipped — piexif does not support it).
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

import piexif

_SUPPORTED = frozenset({'.jpg', '.jpeg', '.tiff'})


def change_image_times(source_dir: str, date_orig: datetime) -> None:
    for root, _, files in os.walk(source_dir):
        for file in sorted(files):
            if Path(file).suffix.lower() not in _SUPPORTED:
                continue
            path = os.path.join(root, file)
            date_orig += timedelta(seconds=1)
            new_date = date_orig.strftime('%Y:%m:%d %H:%M:%S').encode()
            try:
                exif_dict = piexif.load(path)
                exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
                exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
                exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
                piexif.insert(piexif.dump(exif_dict), path)
                print(f'Updated: {path}  →  {date_orig}')
            except Exception as e:
                print(f'Error processing {path}: {e}')


if __name__ == '__main__':
    change_image_times('./test', datetime(2005, 12, 31, 23, 29, 59))
