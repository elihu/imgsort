from __future__ import annotations

import piexif

from imgsort.image import _camera_name, _date_from_exif, _extract_exif, organize_images


def test_prefers_date_time_original_from_exif_sub_ifd(make_jpeg):
    path = make_jpeg(
        ifd0={piexif.ImageIFD.DateTime: b'2020:01:01 00:00:00'},
        exif={piexif.ExifIFD.DateTimeOriginal: b'2010:05:05 10:10:10'},
    )
    info = _date_from_exif(_extract_exif(str(path)), 'Cam')
    assert info == {'year': '2010', 'month': '05', 'stem': '2010_05_05-10_10_10-Cam'}


def test_zeroed_exif_date_falls_through_to_next_tag(make_jpeg):
    path = make_jpeg(
        ifd0={piexif.ImageIFD.DateTime: b'2020:01:01 00:00:00'},
        exif={piexif.ExifIFD.DateTimeOriginal: b'0000:00:00 00:00:00'},
    )
    assert _date_from_exif(_extract_exif(str(path)), 'Cam')['year'] == '2020'


def test_camera_name_is_filename_safe():
    assert _camera_name({'Model': 'Canon EOS/5D\0 Mk II'}) == 'CanonEOS5DMkII'
    assert _camera_name({}) == 'Unknown-Camera'


def test_organize_images_end_to_end_and_idempotent_walk(tmp_path, make_jpeg):
    make_jpeg(
        name='p.jpg',
        ifd0={piexif.ImageIFD.Model: b'Pixel 8'},
        exif={piexif.ExifIFD.DateTimeOriginal: b'2010:05:05 10:10:10'},
    )
    dst = tmp_path / 'sorted' / 'image'
    organize_images(tmp_path, dst)
    organize_images(tmp_path, dst)  # second run must not re-ingest dst
    files = sorted(p.relative_to(dst).as_posix() for p in dst.rglob('*.jpg'))
    assert files == [
        '2010/05/2010_05_05-10_10_10-Pixel8.jpg',
        '2010/05/2010_05_05-10_10_10-Pixel8_1.jpg',
    ]


def test_organize_images_continues_after_copy_error(tmp_path, make_jpeg, monkeypatch, capsys):
    make_jpeg(name='a.jpg')
    make_jpeg(name='b.jpg')
    import imgsort.image as mod

    real_copy = mod.safe_copy
    def flaky(src, *args):
        if src.endswith('a.jpg'):
            raise PermissionError('denied')
        return real_copy(src, *args)
    monkeypatch.setattr(mod, 'safe_copy', flaky)

    organize_images(tmp_path, tmp_path / 'out')
    assert '1 copied, 1 failed' in capsys.readouterr().out
