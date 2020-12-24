# 📺 channels-edl-stripper
Strips commercials off Channels DVR recordings using outputted EDL

## Prerequisites
- Python 3.8+
- pip
- ffmpeg


## Getting Started
```
sudo pip3 install edlstrip
edlstrip movie.mpg
```

## Usage
```
usage: edlstrip [-h] [--vcodec VCODEC] [--acodec ACODEC] [-o OUT_FILE] [--verbose] video [edl]

Strips commercials off Channels DVR recordings using outputted EDL

positional arguments:
  video                 video file to strip
  edl                   EDL file used to control stripping

optional arguments:
  -h, --help            show this help message and exit
  --vcodec VCODEC       the video codec used to trancode (default: copy)
  --acodec ACODEC       the audio codec used to trancode (default: copy)
  -o OUT_FILE, --outfile OUT_FILE
                        the file to write out to (default: <video>_comskipped.mkv)
  --verbose, -v         confirms and disables copy vcodec usage prompt
  ```

## Docker

_Coming Soon_

### docker-compose
```
version: 3
```
