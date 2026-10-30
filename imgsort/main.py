from __future__ import annotations

from pathlib import Path

import typer

from .image import organize_images
from .video import organize_videos

app = typer.Typer(
    pretty_exceptions_show_locals=False,
    help='Sort and organize photo and video galleries by embedded metadata.',
)


@app.command()
def image(
    src: Path = typer.Argument(
        Path('./'), exists=True, file_okay=False, readable=True,
        help='Source directory to scan for images.',
    ),
    dst: Path = typer.Option(
        Path('./sorted/image'), '--dst', '-d',
        help='Destination directory for sorted images.',
    ),
) -> None:
    """
    Sort images (JPG, JPEG, PNG, TIFF) into YEAR/MONTH subfolders.

    \b
    Date resolution priority:
      1. EXIF metadata  (DateTimeOriginal, DateTimeDigitized or DateTime)
      2. Filename pattern  (WhatsApp, Screenshot, Google Photos)
      3. File modification time  (last resort)
    """
    organize_images(src, dst)


@app.command()
def video(
    src: Path = typer.Argument(
        Path('./'), exists=True, file_okay=False, readable=True,
        help='Source directory to scan for videos.',
    ),
    dst: Path = typer.Option(
        Path('./sorted/video'), '--dst', '-d',
        help='Destination directory for sorted videos.',
    ),
) -> None:
    """
    Sort videos (MP4, AVI, MOV, WMV, MPG) into YEAR/MONTH subfolders.

    \b
    Date resolution priority:
      1. Embedded metadata  (via hachoir)
      2. File modification time  (last resort)
    """
    organize_videos(src, dst)


if __name__ == '__main__':
    app()
