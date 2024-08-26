
from datetime import timedelta
from datetime import datetime
import os
import piexif
def organize_images(source_dir, date_orig):
    """ Change metadata with given datetime original."""

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('jpg', 'jpeg', 'png', 'tiff')):
                image_path = os.path.join(root, file)
                exif_dict = piexif.load(image_path)
                date_orig += timedelta(seconds=1)
                new_date = date_orig.strftime("%Y:%m:%d %H:%M:%S")
                exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
                exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
                exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, image_path)

if __name__ == "__main__":
    source_directory = "./test"
    date_orig = datetime(2005, 12, 31, 23, 29, 59)
    organize_images(source_directory, date_orig)
