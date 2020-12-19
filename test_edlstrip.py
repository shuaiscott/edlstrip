import pytest
from unittest.mock import patch, mock_open
from edlstrip import to_timecode, parse_edl

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
    assert to_timecode(seconds) == timecode



@pytest.mark.parametrize("file_data, timecode_tuple_list", [
    ("1 2", [("00:00:01.000", "00:00:02.000")]),
    ("1 2\n1 2", [("00:00:01.000", "00:00:02.000"),("00:00:01.000", "00:00:02.000")]),
    ("1 2\n3 4\n5 6\n7 8\n9 10\n11 12", [("00:00:01.000", "00:00:02.000"),("00:00:03.000", "00:00:04.000"),("00:00:05.000", "00:00:06.000"),("00:00:07.000", "00:00:08.000"),("00:00:09.000", "00:00:10.000"),("00:00:11.000", "00:00:12.000")]),
    ("1 2.223", [("00:00:01.000", "00:00:02.223")]),
    ("1 1.1111111111111", [("00:00:01.000", "00:00:01.111")]),
])
def test_parse_edl(file_data, timecode_tuple_list):
    with patch('builtins.open', mock_open(read_data=file_data)):
        edl_list = parse_edl('mocked params')
        assert edl_list == timecode_tuple_list
    
