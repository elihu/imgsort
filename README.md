# Image and Video Sort (imgsort)

A Python 3 tool with a user-friendly interface (Typer) designed to sort and organize your photo and video galleries based on their embedded metadata.

[![License: Apache-2.0][license-img]][license] [![GitHub Release][release-img]][release]

### Features:

Supports image formats like JPEG, PNG, etc. (using Pillow)
Handles video formats like MP4, AVI, etc. (using Hachoir)
Offers flexibility with various sorting options based on metadata (e.g., date taken, location, camera model)
Installation:

### Install dependencies:

The tool is using [Typer](https://typer.tiangolo.com/tutorial/)

- Install typer 
```bash
pip install "typer[all]"
```

The tool is using [Poetry](https://python-poetry.org)

- Install poetry 
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
> ❗ **Disclaimer:** Use the installation script at your own risk, it is recommended to read and understand an installation script before execution.

### Build and install the tool:

> ⚠️ Instructions for Linux users

Clone this repository:

```bash
git clone https://github.com/elihu/imgsort.git
cd imgsort
```
Using a Makefile to build and install the tool locally. 

```bash
make install
```

Also to uninstall just:

```bash
make uninstall
```

### Usage:

The tool comes with two main commands: image and video.

> `imgsort image`: Sorts images within a directory based on metadata.
> `imgsort video`: Sorts videos within a directory based on metadata.

For both commands, you can use the following options:


> `--src:` Specifies the source directory containing the files to be sorted. Defaults to the current directory (`./`)
> `--dst:` Specifies the destination directory where the sorted files will be placed. Defaults to `./sorted/image` for images and `./sorted/video` for videos.

### Example Usage:

```bash
# Sort images in the current directory and place them in a subdirectory called "sorted/image"
imgsort image

# Sort videos in a specific directory and place them in a custom destination directory
imgsort video --src "/path/to/videos" --dst "/path/to/organized_videos"
```

### How it Works (Image and Video Sorting):

#### Image sorting
The organize_images function is the heart of the image sorting process. Here's a breakdown of its steps:

1. **Checks Destination Directory:** It verifies if the destination directory exists and creates it if not.
1. **Loops through Files:** It iterates through all files within the source directory.
1. **Filters Images:** It checks for image file extensions (JPG, JPEG, PNG, TIFF) before proceeding.
1. **Extracts Metadata:** It uses the Pillow library to extract metadata like camera model and date taken from the image.
1. **Handles Missing Dates:** If the standard date tags are missing, it attempts to extract the date using regular expressions from filenames based on patterns commonly used by messaging apps (WhatsApp) or cloud storage services (Google Photos).
1. **Creates Destination Folder Structure:** Based on the extracted date (year and month), it creates subfolders within the destination directory.
1. **Creates Unique Filename:** It constructs a new filename combining the extracted date and camera model (if available).
1. **Copies Files:** It copies the image file to the newly created destination folder with the unique filename.

#### Video sorting
The *organize_videos* function is the heart of the video sorting process. Here's a breakdown of its steps:

1. **Checks Destination Directory:** It verifies if the destination directory exists and creates it if not.
1. **Loops through Files:** It iterates through all files within the source directory.
1. **Filters Videos:** It checks for video file extensions (AVI, MP4, MPG, WMV, MOV) before proceeding.
1. **Checks File Size:** It skips zero-byte files to avoid unnecessary processing.
1. **Creates Parser:** It initializes a parser object using the createParser function (specific implementation details might vary depending on the video metadata extraction library used).
1. **Extracts Metadata:** It uses the parser to extract metadata from the video file, including the creation date. If metadata extraction fails, it continues to the next step.
1. **Handles Missing Dates:** If the creation date is not found in the metadata, it attempts to extract it from the filename using regular expressions or the file's modification time.
1. **Creates Destination Folder Structure:** Based on the extracted date (year and month), it creates subfolders within the destination directory.
1. **Creates Unique Filename:** It constructs a new filename combining the extracted date.
1. **Copies Files:** It copies the video file to the newly created destination folder with the unique filename.

<!-- 
### Contributing:

We welcome contributions to improve this tool! Please refer to the CONTRIBUTING.md file for guidelines. -->

### License:

This project is licensed under the MIT License (see [LICENSE] for details).

[license]: https://github.com/elihu/imgsort/blob/main/LICENSE
[license-img]: https://img.shields.io/badge/License-Apache%202.0-blue.svg
[release]: https://github.com/elihu/imgsort/releases
[release-img]: https://img.shields.io/github/release/elihu/imgsort.svg?logo=github