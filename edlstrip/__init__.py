import os, sys, subprocess, logging
import argparse
import tempfile
import click

## 
# Helper functions
##
def parse_args(input_args):
    """
    Parses commandline arguments and provides help/interface info

    Throws error if required file arguments don't exist on filesystem
    """
    parser = argparse.ArgumentParser(prog='edlstrip', description='Strips commercials off Channels DVR recordings using outputted EDL')
    parser.add_argument('video', type=str,
                        help='video file to strip')
    parser.add_argument('edl', type=str, nargs="?",
                        help='EDL file used to control stripping')
    parser.add_argument('--vcodec', dest='vcodec', default='copy',
                        help='the video codec used to trancode (default: copy)')
    parser.add_argument('--acodec', dest='acodec', default='copy',
                        help='the audio codec used to trancode (default: copy)')
    parser.add_argument('-o','--outfile', dest='out_file',
                        help='the file to write out to (default: <video>_comskipped.mkv)')
    parser.add_argument('--verbose', '-v', action='count', default=1,
                        help='confirms and disables copy vcodec usage prompt')
    args = parser.parse_args()

    # set args.edl to same as video, with the extension swapped
    if args.edl == None:
        base_name = os.path.splitext(os.path.basename(args.video))[0]
        args.edl = os.path.join(os.path.dirname(args.video), base_name + ".edl")

    # Modify loglevel
    args.verbose = 30 - (10*args.verbose) if args.verbose > 0 else 0

    # Determine out_file name if None
    if args.out_file is None:
        args.out_file = os.path.join(os.path.dirname(args.video), resolve_out_filename(args.video))

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
    # Convert input to float
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
    logging.info(f"Opening {edlfile}...")
    with open(edlfile) as fp:
        line = fp.readline()
        cnt = 0
        while line:
            start, stop, linetype = line.split()
            logging.debug(f"Split EDL line to {start}-{stop} with LineType: {linetype}")
            if linetype == "3":
                tc_start = to_timecode(start)
                tc_stop = to_timecode(stop)
                edl_tuple = (tc_start, tc_stop)
                logging.debug(f"Created tuple: {edl_tuple}")
                edl_item_list.append(edl_tuple)
            line = fp.readline()
            cnt += 1
        logging.info(f"Read {cnt} lines from {edlfile}")
    return edl_item_list


def get_video_length(input_video):
    """
    Extracts the duration/length of the video we're splitting
    """
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_video], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    length = float(result.stdout)
    logging.debug(f"Length of {input_video}: {length}s")
    return length


def invert_edl_list(timecode_list, end_timecode):
    """
    Inverts the list of timecodes from the EDL file.
    Used to determine which splits to make and keep
    """
    current_tc = "00:00:00.000"
    inverted = []

    for start,stop in timecode_list:
        if start == current_tc:
            current_tc = stop # Skips ahead if there isn't any good content inbetween timecodes
        else:
            inverted.append((current_tc,start))
            current_tc = stop
    
    inverted.append((current_tc, end_timecode))

    return inverted


def split_video(video_file, edl_list, split_dir, vcodec='libx264', acodec='copy', verbosity=0):
    """
    uses ffmpeg commandline to split the file based on edl tuple (quick method by copying, so will split by i-frames)
    """
    split_cnt = 1
    split_list = []
    for item in edl_list:
        start,stop = item
        split_file = os.path.join(split_dir, f"split{split_cnt}.ts")
        logging.info(f"Splitting using Start: {start}, Stop: {stop} to split{split_cnt}.ts")
        cmd = f"ffmpeg -hide_banner -loglevel {str(verbosity)} -y -i '{video_file}' -acodec {acodec} -vcodec {vcodec} -ss {start} -to {stop} -reset_timestamps 1 '{split_file}'"
        logging.debug(f"Running command: {cmd}")
        subprocess.check_call(['ffmpeg','-hide_banner','-loglevel',str(verbosity),'-y','-i',video_file,'-acodec',acodec,'-vcodec',vcodec,'-ss',start,'-to',stop,'-reset_timestamps','1',split_file])
        split_list.append(split_file)
        split_cnt+=1
    return split_list
    # HALP, ffmpeg-python doesn't let you seek like:
    # ffmpeg -ss 00:01:00 -i input.mp4 -to 00:02:00 -c copy output.mp4
    # https://stackoverflow.com/a/42827058
    #
    # video = ffmpeg.input('CreuxDeVan.mpg')
    # trimmed = ffmpeg.trim(video, start=0, duration=1)
    # out = ffmpeg.output(trimmed, 'test.mpg', vcodec='copy', acodec='copy')
    # out.run()


def join_video(split_list, out_file, verbosity=0):
    """
    Uses ffmpeg commandline to join the files together (quick method by copying)
    """
    join_str = ''.join([f"file '{os.path.abspath(file)}'\n" for file in split_list])
    logging.debug(f"Join Files: \n{join_str}")

    # Create temp file to store concat data
    fp = tempfile.NamedTemporaryFile(delete=False)
    fp.write(join_str.encode('utf-8'))
    fp.close()

    # "ffmpeg -f concat -safe 0 -i '{fp.name}' -c copy '{out_file}'"
    logging.debug(f"Created temp file: {fp.name}")
    logging.info(f"Joining {len(split_list)} files to {out_file}")
    subprocess.check_call(['ffmpeg', '-hide_banner', '-loglevel', str(verbosity), '-f', 'concat', '-safe', '0', '-i', fp.name, '-c', 'copy', out_file])
    
    # Delete temp file as we're done with it
    os.remove(fp.name)

    
def resolve_out_filename(input_file_name):
    """
    Resolves the appropriate output file name based on video input name
    """
    base_name = os.path.splitext(os.path.basename(input_file_name))[0]
    
    extension = '.mkv'

    return f"{base_name}_comskipped{extension}"

def intro_log(args):
    print(
    "\n" +
    "          _ _     _        _       \n" + 
    "  ___  __| | |___| |_ _ __(_)_ __  \n" +
    " / _ \\/ _` | / __| __| '__| | '_ \\ \n" +
    "|  __/ (_| | \\__ \\ |_| |  | | |_) |\n" +
    " \\___|\\__,_|_|___/\\__|_|  |_| .__/ \n" +
    "                            |_|    \n"
    )
    print(f"Video: {args.video}")
    print(f"EDL: {args.edl}")
    print(f"vcodec: {args.vcodec}")
    print(f"acodec: {args.acodec}")
    print(f"Output: {args.out_file}\n")


def main():
    """
    Main Execution
    """
    # Parse Args
    args = parse_args(sys.argv[1:])

    # Setup Logger
    logging.basicConfig(level=args.verbose, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Log arguments/work to be done
    intro_log(args)

    #  Check if codec is copy, then write message that cuts won't be precise if input file has I-frames
    if 'copy' in args.vcodec:
        logging.warning('Copy vcodec was selected. This provides a faster split, but is not as accurate.')

    # Parse EDL file
    edl_list = parse_edl(args.edl)

    # Get end timecode of file
    end_timecode = to_timecode(get_video_length(args.video))

    # Invert edl file 
    inverted_list = invert_edl_list(edl_list, end_timecode)

    # Create temp directory for split files
    with tempfile.TemporaryDirectory() as tmpdirname:
        logging.debug(f"Created temporary directory '{tmpdirname}'")

        # Split video file by edl list
        split_file_list = split_video(args.video, inverted_list, tmpdirname, args.vcodec, args.acodec)

        # Join split videos together again
        join_video(split_file_list, args.out_file)




