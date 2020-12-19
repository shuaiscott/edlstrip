import ffmpeg
import os
import argparse

###
# Parse Args
###
parser = argparse.ArgumentParser(description='Strips commercials off Channels DVR recordings using outputted EDL')
parser.add_argument('video', type=str,
                    help='video file to strip')
parser.add_argument('edl', type=str,
                    help='EDL file used to control stripping')
parser.add_argument('--vcodec', dest='vcodec',
                    help='the video codec to transcode file to')
parser.add_argument('--acodec', dest='acodec',
                    help='the audio codec to transcode file to')
args = parser.parse_args()

def to_timecode(seconds):
    """
    input: seconds
    from: https://stackoverflow.com/a/21520196
    """
    return '{:02}:{:02}:{:02}'.format(seconds//3600, seconds%3600//60, seconds%60)


# HALP, ffmpeg-python doesn't let you seek like:
# ffmpeg -ss 00:01:00 -i input.mp4 -to 00:02:00 -c copy output.mp4
# https://stackoverflow.com/a/42827058
#
# video = ffmpeg.input('CreuxDeVan.mpg')
# trimmed = ffmpeg.trim(video, start=0, duration=1)
# out = ffmpeg.output(trimmed, 'test.mpg', vcodec='copy', acodec='copy')
# out.run()




