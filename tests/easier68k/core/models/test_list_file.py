import pytest

from easier68k.core.models.list_file import ListFile

def test_load_data_at_location():
    data = [0x01, 0x02, 0x03, 0x04, 0x05]
    location = 0x0001000

    lf = ListFile()

    lf._load_data_at_location(location, data)

    # check that the data is loaded proper
    assert lf.content[location] == 0x01
    assert lf.content[location + 1] == 0x02
    assert lf.content[location + 2] == 0x03
    assert lf.content[location + 3] == 0x04
    assert lf.content[location + 4] == 0x05