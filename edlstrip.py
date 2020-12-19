import os, sys, logging
import argparse
import ffmpeg

###
# Parse Args
###


## 
# Helper functions
##
def parse_args(args):
    """
    Parses commandline arguments and provides help/interface info

    Throws error if required file arguments don't exist on filesystem
    """
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

    # Check file existence
    if (not os.path.exists(args.video)):
        sys.exit(f"Error: Video file '{args.video}' doesn't exist")
    if (not os.path.exists(args.edl)):
        sys.exit(f"Error: EDL file '{args.edl}' doesn't exist")
    return args
        

def to_timecode(input_seconds):
    """
    input: seconds
    from: https://stackoverflow.com/a/21520196
    """
    # Convert input to float ("Break in case of Strings")
    seconds = float(input_seconds)

    decimal = round(seconds % 1, 3) # round to 3 decimals to help with floating point errors
    int_seconds = int(round(seconds - decimal))
    undecimal = int(decimal * 1000)
    return '{:02}:{:02}:{:02}.{:03}'.format(int_seconds//3600, int_seconds%3600//60, int_seconds%60, undecimal)

def parse_edl(edlfile):
    """
    input edl file to parse
    """
    edl_item_list = []
    with open(edlfile) as fp:
        line = fp.readline()
        cnt = 0
        while line:
            start, stop = line.split()[:2]
            logging.debug(f"Split EDL line to {start},{stop}")
            tc_start = to_timecode(start)
            tc_stop = to_timecode(stop)
            edl_tuple = (tc_start, tc_stop)
            logging.debug(f"Created tuple: {edl_tuple}")
            edl_item_list.append(edl_tuple)
            line = fp.readline()
            cnt += 1
        logging.info(f"Read {cnt} lines from {edlfile}")
    return edl_item_list
##
# Main Execution
##
if __name__ == '__main__':
    # Parse Args
    parser = parse_args(sys.argv[1:])

    # Setup Logger
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')



    # HALP, ffmpeg-python doesn't let you seek like:
    # ffmpeg -ss 00:01:00 -i input.mp4 -to 00:02:00 -c copy output.mp4
    # https://stackoverflow.com/a/42827058
    #
    # video = ffmpeg.input('CreuxDeVan.mpg')
    # trimmed = ffmpeg.trim(video, start=0, duration=1)
    # out = ffmpeg.output(trimmed, 'test.mpg', vcodec='copy', acodec='copy')
    # out.run()




