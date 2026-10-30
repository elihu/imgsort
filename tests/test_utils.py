from __future__ import annotations

from datetime import datetime

import pytest

from imgsort.utils import date_from_filename, date_info, is_plausible, safe_copy, walk_files


@pytest.mark.parametrize(
    ('filename', 'expected'),
    [
        ('IMG-20240115-WA0012.jpg', {'year': '2024', 'month': '01', 'stem': '2024_01_15-00_12-WA'}),
        ('IMG_20240115_1234.jpg', {'year': '2024', 'month': '01', 'stem': '2024_01_15-12_34-WA'}),
        ('20240115-1234.jpg', {'year': '2024', 'month': '01', 'stem': '2024_01_15-12_34-GPhotos'}),
        ('Screenshot_2024-01-15-12-34.png',
         {'year': 'Screenshots', 'month': None, 'stem': '2024_01_15-12_34-Screenshot'}),
    ],
)
def test_date_from_filename_patterns(filename, expected):
    assert date_from_filename(filename) == expected


@pytest.mark.parametrize(
    'filename', ['20244599-1234.jpg', 'IMG-20241332-WA0001.jpg', 'holiday.jpg'],
)
def test_date_from_filename_rejects_invalid_dates(filename):
    assert date_from_filename(filename) is None


def test_is_plausible_bounds():
    assert is_plausible(datetime(2010, 5, 5))
    assert not is_plausible(datetime(1, 1, 1))
    assert not is_plausible(datetime(datetime.now().year + 2, 1, 1))


def test_date_info_format():
    info = date_info(datetime(2010, 5, 5, 10, 10, 10), 'Cam')
    assert info == {'year': '2010', 'month': '05', 'stem': '2010_05_05-10_10_10-Cam'}


def test_safe_copy_appends_suffix_on_collision(tmp_path):
    src = tmp_path / 'a.jpg'
    src.write_bytes(b'x')
    out = tmp_path / 'out'
    first = safe_copy(str(src), str(out), 'stem', '.jpg')
    second = safe_copy(str(src), str(out), 'stem', '.jpg')
    assert first.endswith('stem.jpg')
    assert second.endswith('stem_1.jpg')


def test_walk_files_skips_destination_inside_source(tmp_path):
    (tmp_path / 'a.jpg').write_bytes(b'x')
    (tmp_path / 'sorted' / 'image' / '2020').mkdir(parents=True)
    (tmp_path / 'sorted' / 'image' / '2020' / 'b.jpg').write_bytes(b'x')
    (tmp_path / 'notes.txt').write_text('x')
    found = list(walk_files(tmp_path, tmp_path / 'sorted' / 'image', frozenset({'.jpg'})))
    assert [p.split('/')[-1] for p in found] == ['a.jpg']
