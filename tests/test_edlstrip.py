import pytest
import os, subprocess
from unittest.mock import patch, mock_open
import edlstrip


@pytest.mark.parametrize("seconds, timecode", [
    (3600, '01:00:00.000'),
    ('3600', '01:00:00.000'),
    (0, '00:00:00.000'),
    (100, '00:01:40.000'),
    (1000, '00:16:40.000'),
    (36001, '10:00:01.000'),
    (3600.500, '01:00:00.500'),
    (3600.2500, '01:00:00.250'),
])
def test_to_timecode(seconds, timecode):
    assert edlstrip.to_timecode(seconds) == timecode


@pytest.mark.parametrize("file_data, timecode_tuple_list", [
    ("1 2  3", [("00:00:01.000", "00:00:02.000")]),
    ("1 2   3\n1 2   3", [("00:00:01.000", "00:00:02.000"),("00:00:01.000", "00:00:02.000")]),
    ("1 2  3\n3 4  3\n5 6 3\n7 8 3\n9 10 3\n11 12 3", [("00:00:01.000", "00:00:02.000"),("00:00:03.000", "00:00:04.000"),("00:00:05.000", "00:00:06.000"),("00:00:07.000", "00:00:08.000"),("00:00:09.000", "00:00:10.000"),("00:00:11.000", "00:00:12.000")]),
    ("1 2.223 3", [("00:00:01.000", "00:00:02.223")]),
    ("1 1.1111111111111 3", [("00:00:01.000", "00:00:01.111")]),
    ("1 2  4", []),
])
def test_parse_edl(file_data, timecode_tuple_list):
    with patch('builtins.open', mock_open(read_data=file_data)):
        edl_list = edlstrip.parse_edl('mocked params')
        assert edl_list == timecode_tuple_list


def test_parse_edl_real():
    edl_list = edlstrip.parse_edl('./tests/test_assets/CreuxDeVan.edl')
    assert edl_list == [('00:00:00.000','00:00:00.750'),('00:00:00.750','00:00:02.000'),('00:00:02.000','00:00:03.000')]


@pytest.mark.parametrize("timecode_list, end_timecode, inverted_list", [
    ([("00:00:01.000", "00:00:02.000")], "00:00:03.000", [("00:00:00.000","00:00:01.000"), ("00:00:02.000","00:00:03.000")]),
    ([("00:00:00.000", "00:00:02.000")], "00:00:03.000", [("00:00:02.000","00:00:03.000")]),
    ([], "00:00:03.000", [("00:00:00.000","00:00:03.000")]),
    ([("00:00:00.000", "00:00:00.000")], "00:00:03.000", [("00:00:00.000","00:00:03.000")]),

])
def test_invert_edl_list(timecode_list, end_timecode, inverted_list):
    assert inverted_list == edlstrip.invert_edl_list(timecode_list, end_timecode)


@pytest.mark.parametrize("codec, duration", [
    ('copy', '0.560000'), # test case for inaccurate copy with I-frames
    ('libx264', '1.000000'),
])
def test_split_video_1s(codec, duration):
    tempdir = './splitfiles/'
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
    file_list = edlstrip.split_video('./tests/test_assets/CreuxDeVan.mpg',[('00:00:00.000', '00:00:01.000')], 
                                    tempdir, codec, 'copy')
    assert file_list == [tempdir + 'split1.ts']

    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {file_list[0]}"
    process = subprocess.Popen(cmd, shell=True,
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
    split_length, err = process.communicate()
    assert split_length.decode('ascii').strip() == duration

    # Cleanup
    os.remove(file_list[0])
    os.rmdir(tempdir)


def test_join_video():
    split_list = ['./tests/test_assets/split1.ts','./tests/test_assets/split2.ts','./tests/test_assets/split3.ts']
    out_file = './tests/testjoin.mp4'
    edlstrip.join_video(split_list, out_file)
    assert os.path.exists(out_file)

    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {out_file}"
    process = subprocess.Popen(cmd, shell=True,
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
    video_length, err = process.communicate()
    assert video_length.decode('ascii').strip() == "3.000000"

    os.remove(out_file)


@pytest.mark.parametrize("filename, out_filename", [
    ('vid.mp4', 'vid_comskipped.mkv'),
    ('vid.asdf', 'vid_comskipped.mkv'), # Let's make ffmpeg worry about codecs and shove into MKV container
    ('stuff.mp4', 'stuff_comskipped.mkv'),
    ('vid.avi', 'vid_comskipped.mkv'),
    ('episode.mpg', 'episode_comskipped.mkv'),
])
def test_resolve_out_filename(filename, out_filename):
    assert out_filename == edlstrip.resolve_out_filename(filename)