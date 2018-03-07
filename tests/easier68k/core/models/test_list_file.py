import pytest

from easier68k.core.models.list_file import ListFile

def test_insert_data():
    """
    General tests of the list file operation
    :return:
    """

    # create a new ListFile
    a = ListFile()

    # try to insert in bounds
    a.insert_data(0x3100, '1234ABCD')

    # try to insert out of bounds
    with pytest.raises(AssertionError):
        a.insert_data(-1, 'aaaa')

    with pytest.raises(AssertionError):
        a.insert_data(16777217, 'aaaa')

    # try to insert bogus data
    with pytest.raises(ValueError):
        a.insert_data(123, 'ABCDEFG')