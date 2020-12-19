import pytest
from edlstrip import to_timecode

@pytest.mark.parametrize("seconds, timecode", [
    (3600, '01:00:00'),
    (0, '00:00:00'),
    (100, '00:01:40'),
    (1000, '00:16:40'),
    (36001, '10:00:01'),
])
def test_to_timecode(seconds, timecode):
    assert to_timecode(seconds) == timecode