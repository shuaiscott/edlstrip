# 📺 channels-edl-stripper
Strips commercials off Channels DVR recordings using outputted EDL

## Prerequisites
- Python 3.8+
- pip
- ffmpeg


## Getting Started
```
pip install -r requirements.txt
python edlstrip.py movie.mpg movie.epg --vcodec libx264 -o movie_comskipped.mp4
```

## Usage
```
usage: edlstrip.py [-h] [--vcodec VCODEC] [--acodec ACODEC] [-o OUT_FILE] [--confirm-copy] video edl

Strips commercials off Channels DVR recordings using outputted EDL

positional arguments:
  video                 video file to strip
  edl                   EDL file used to control stripping

optional arguments:
  -h, --help            show this help message and exit
  --vcodec VCODEC       the video codec used to trancode (default: libx264)
  --acodec ACODEC       the audio codec used to trancode (default: copy)
  -o OUT_FILE, --outfile OUT_FILE
                        the file to write out to (default: <video>_comskipped.mkv)
  --confirm-copy        confirms and disables copy vcodec usage prompt
  ```

## Docker

_Coming Soon_

### docker-compose
```
version: 3
```
