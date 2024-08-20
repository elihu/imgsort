import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

def extract_metadata(image_path):
    """Extrae los metadatos de una imagen y devuelve un diccionario."""
    image = Image.open(image_path)
    exif_data = image._getexif()

    metadata = {}
    if exif_data is not None:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            metadata[tag_name] = value
    return metadata

def organize_images(source_dir, dest_dir):
    """Organiza las imágenes en carpetas basadas en sus metadatos."""
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('jpg', 'jpeg', 'png', 'tiff')):
                image_path = os.path.join(root, file)
                metadata = extract_metadata(image_path)
                
                # print(metadata)
                
                # Extraer el modelo de la cámara
                camera_model = metadata.get('Model', 'Unknown-Camera').replace(' ', '')

                # Extraer la fecha de creación
                date_taken = metadata.get('DateTimeOriginal')
                year_taken = ""
                if date_taken:
                    date_taken = date_taken.replace(':', '-').split(' ')[0]
                    newname = f"{metadata.get('DateTimeOriginal').replace(':', '_').replace(' ', '-')}-{camera_model}"
                    year_taken = date_taken.split('-')[0]
                    month_taken = date_taken.split('-')[1]
                else:
                    #intentar sacar fechas del filename con regex sino ya ir con el mtime
                    m_time = os.path.getmtime(image_path)
                    if m_time:
                        date_taken = str(datetime.fromtimestamp(m_time))
                        newname = f"{date_taken.replace('-', '_').replace(':', '_').replace(' ', '-')}-{camera_model}"
                        year_taken = date_taken.split('-')[0]
                        month_taken = date_taken.split('-')[1]
                    else:
                        date_taken = "Unknown-Date"
                        newname = file

                # Crear el camino de la carpeta de destino
                if year_taken:
                    target_folder = os.path.join(dest_dir, year_taken, month_taken)
                else:
                    target_folder = os.path.join(dest_dir, date_taken)

                # Crear las carpetas si no existen
                os.makedirs(target_folder, exist_ok=True)

                # Copia el archivo a la nueva ubicación con nombre normalizado
                print(f'Copiando: {image_path} -> {newname}')
                shutil.copy(image_path, os.path.join(target_folder, newname))

                print(f'Copiado: {file} -> {target_folder}')

if __name__ == "__main__":
    source_directory = "./original"
    destination_directory = "./organizada"

    organize_images(source_directory, destination_directory)
