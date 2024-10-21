import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import re
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from rich import print
import typer
import calendar

app = typer.Typer()

# Internal functions
def extract_metadata(image_path):
    """Extracts image metadata and returns a dict."""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
    except:
        return {}

    metadata = {}
    if exif_data is not None:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            metadata[tag_name] = value
    return metadata

def organize_images(source_dir, dest_dir):
    """Organize images in directories based on metadata."""
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('jpg', 'jpeg', 'png', 'tiff')):
                image_path = os.path.join(root, file)
                metadata = extract_metadata(image_path)
                
                # print(metadata)
                
                # Extracts camera model
                camera_model = metadata.get('Model', 'Unknown-Camera').replace(' ', '').replace('\0', '')

                # Extracts creation date
                date_taken = metadata.get('DateTimeOriginal')
                if not date_taken:
                    date_taken = metadata.get('DateTime')
                year_taken = ""
                if date_taken:
                    newname = f"{date_taken.replace(':', '_').replace(' ', '-')}-{camera_model}"
                    date_taken = date_taken.replace(':', '-').split(' ')[0]
                    year_taken = date_taken.split('-')[0]
                    month_taken = date_taken.split('-')[1]
                else:
                    # tries to get creation date from filename with regex if not, tries to get modification time
                    whatsapp_img = r'IMG-(\d{4})(\d{2})(\d{2})-WA(\d{2})(\d{2})'
                    whatsapp_old = r'IMG_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})'
                    match = re.search(whatsapp_img, file) or re.search(whatsapp_old, file)
                    if match:
                        date_taken = f'{match.group(1)}-{match.group(2)}-{match.group(3)} {match.group(4)}:{match.group(5)}'
                        year_taken = match.group(1)
                        month_taken = match.group(2)
                        newname = f'{match.group(1)}_{match.group(2)}_{match.group(3)}-{match.group(4)}_{match.group(5)}-WA'
                    else:
                        screenshot = r'Screenshot_(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})'
                        match = re.search(screenshot, file) 
                        if match:      
                            date_taken = 'Screenshots'
                            newname = f'{match.group(1)}_{match.group(2)}_{match.group(3)}-{match.group(4)}_{match.group(5)}-Screenshot'
                        else:
                            gphotos_old = r'(20\d{2})(\d{2})(\d{2})-00(\d{2})(\d{2})'
                            gphotos = r'(20\d{2})(\d{2})(\d{2})-(\d{2})(\d{2})'
                            match = re.search(gphotos_old, file) or re.search(gphotos, file)
                            if match:
                                date_taken = f'{match.group(1)}-{match.group(2)}-{match.group(3)} {match.group(4)}:{match.group(5)}'
                                year_taken = f'{match.group(1)}'
                                month_taken = match.group(2)
                                newname = f'{match.group(1)}_{match.group(2)}_{match.group(3)}-{match.group(4)}_{match.group(5)}-GPhotos'
                            else:
                                # mtime date
                                m_time = os.path.getmtime(image_path)
                                if m_time:
                                    date_taken = str(datetime.fromtimestamp(m_time))
                                    newname = f"{date_taken.replace('-', '_').replace(':', '_').replace(' ', '-')}-{camera_model}"
                                    year_taken = date_taken.split('-')[0]
                                    month_taken = date_taken.split('-')[1]
                                else:
                                    date_taken = "Unknown-Date"
                                    newname = file

                # Creates dest dir
                if year_taken:
                    target_folder = os.path.join(dest_dir, year_taken, month_taken)
                else:
                    target_folder = os.path.join(dest_dir, date_taken)

                # Creates dirs if not exist
                os.makedirs(target_folder, exist_ok=True)

                # Copies file to new dest with normalized name
                print(f'Copying: {image_path} -> {newname}')
                try:
                    shutil.copy2(image_path, os.path.join(target_folder, newname))
                except Exception as e:
                    print(f'Error while builtin copy: {e}')
                # print(f'Copiado: {file} -> {target_folder}')

def organize_videos(source_dir, dest_dir):
    """Organize videos in directories based on metadata."""
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('avi', 'mp4', 'mpg', 'wmv', 'mov')):
                year_taken = ''
                video_path = os.path.join(root, file)
                if os.path.getsize(video_path) == 0:
                    print("Warn. Skipping null size file")
                    continue
                parser = createParser(video_path)
                if not parser:
                    print("Unable to parse file %s" % video_path)
                    continue
                with parser:
                    try:
                        metadata = extractMetadata(parser)
                    except Exception as err:
                        print("Metadata extraction error: %s" % err)
                        metadata = None
                if metadata:
                    for line in metadata.exportPlaintext():
                        if line.split(':')[0].lower() == '- creation date':
                            date_taken = datetime.strptime(line.split('date: ')[1], "%Y-%m-%d %H:%M:%S")
                            newname = f"{str(date_taken).replace('-', '_').replace(':', '_').replace(' ', '-')}"
                            year_taken = str(date_taken.year)
                            if year_taken == '1904':
                                year_taken = ''
                            month_taken = f'{str(date_taken.month)}-{calendar.month_abbr[date_taken.month]}'

                if not year_taken:
                    # mtime date
                    m_time = os.path.getmtime(video_path)
                    if m_time:
                        date_taken = datetime.fromtimestamp(m_time)
                        newname = f"{str(date_taken).replace('-', '_').replace(':', '_').replace(' ', '-')}"
                        year_taken = str(date_taken.year)
                        month_taken = f'{str(date_taken.month)}-{calendar.month_abbr[date_taken.month]}'
                    else:
                        date_taken = "Unknown-Date"
                        newname = file
        
                # Creates dest dir
                if year_taken:
                    target_folder = os.path.join(dest_dir, year_taken, month_taken)
                else:
                    target_folder = os.path.join(dest_dir, str(date_taken))

                # Creates dirs if not exist
                os.makedirs(target_folder, exist_ok=True)

                # Copies file to new dest with normalized name
                # print(f'Copying: {video_path} -> {target_folder}')
                try:
                    shutil.copy2(video_path, os.path.join(target_folder, newname))
                except Exception as e:
                    print(f'Error while builtin copy: {e}')
                # print(f'Copiado: {file} -> {target_folder}')
# Callback
@app.callback()
def callback():
    """
    Image and video sorting and organizing tool
    """

# Commands 
@app.command() 
def video(src:str='./', dst:str='./sorted/video'):
    """
    Video sorting and organizing tool. Organize videos in directories based on metadata.
    """
    organize_videos(src, dst)

@app.command() 
def image(src:str='./', dst:str='./sorted/image'):
    """
    Image sorting and organizing tool. Organize images in directories based on metadata.
    """
    organize_images(src, dst)
if __name__ == "__main__":
    app()
