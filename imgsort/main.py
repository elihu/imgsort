from __future__ import annotations

import typer

from .image import organize_images
from .video import organize_videos

app = typer.Typer(
    pretty_exceptions_show_locals=False,
    help='Sort and organize photo and video galleries by embedded metadata.',
)


@app.command()
def image(
    src: str = typer.Argument('./', help='Source directory to scan for images.'),
    dst: str = typer.Option(
        './sorted/image', '--dst', '-d',
        help='Destination directory for sorted images.',
    ),
) -> None:
    """
    Sort images (JPG, JPEG, PNG, TIFF) into YEAR/MONTH subfolders.

    \b
    Date resolution priority:
      1. EXIF metadata  (DateTimeOriginal or DateTime)
      2. Filename pattern  (WhatsApp, Screenshot, Google Photos)
      3. File modification time  (last resort)
    """
    organize_images(src, dst)


@app.command()
def video(
    src: str = typer.Argument('./', help='Source directory to scan for videos.'),
    dst: str = typer.Option(
        './sorted/video', '--dst', '-d',
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
