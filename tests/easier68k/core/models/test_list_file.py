import pytest
import json

from easier68k.core.models.list_file import ListFile

def test_insert_data():
    """
    Tests of ListFile insert
    :return:
    """

    # create a new ListFile
    a = ListFile()

    # try to insert in bounds
    a.insert_data(0x3100, '1234ABCD')

    # try to insert duplicate data (should work silently)
    a.insert_data(0x3100, '12341234')

    # try to insert out of bounds
    with pytest.raises(AssertionError):
        a.insert_data(-1, 'aaaa')

    with pytest.raises(AssertionError):
        a.insert_data(16777217, 'aaaa')

    # try to insert bogus data
    with pytest.raises(ValueError):
        a.insert_data(123, 'ABCDEFG')

    # try to insert garbage
    with pytest.raises((TypeError, ValueError)):
        a.insert_data('123', 123)

    # get starting data
    assert a.get_starting_data(0x3100) is '12341234'

    # out of bounds
    with pytest.raises(AssertionError):
        a.get_starting_data(-1)

    with pytest.raises(AssertionError):
        a.get_starting_data(16777217)

    # not defined
    with pytest.raises(AssertionError):
        a.get_starting_data(0x3200)


def test_insert_data_at_symbol():
    """
    Tests the insert data at symbol method
    :return:
    """

    # create the list file
    a = ListFile()
    # define a symbol
    a.define_symbol('sym', 123)

    # insert some data at that symbol
    a.insert_data_at_symbol('sym', 'ABCD')

    # insert again
    a.insert_data_at_symbol('sym', 'DEDE')

    # insert garbage
    with pytest.raises((TypeError, ValueError)):
        a.insert_data_at_symbol('sym', 123)

    # try to insert at a symbol that doesn't exist
    with pytest.raises(AssertionError):
        a.insert_data_at_symbol('nadda', 'AAAA')


    # use get symbol data
    assert a.get_symbol_data('sym') is 'DEDE'

    with pytest.raises(AssertionError):
        a.get_symbol_data('doesnotexist')


def test_clear_location():
    """
    Tests clear location
    :return:
    """

    a = ListFile()

    # try to clear location that isnt defined
    with pytest.raises(AssertionError):
        a.clear_location(1234)

    a.insert_data(1234, 'AAAA')

    assert a.get_starting_data(1234) is 'AAAA'

    a.clear_location(1234)

    with pytest.raises(AssertionError):
        a.get_starting_data(1234)


def test_symbols():
    """
    Define symbol
    :return:
    """
    a = ListFile()

    a.define_symbol('valid', 1234)
    a.define_symbol('valid', 1234)
    a.define_symbol('valid', 1234)
    a.define_symbol('VALID', 1234)
    a.define_symbol('_valid', 1234)
    a.define_symbol('valid_', 1234)
    a.define_symbol('v_a_l_i_d', 1234)

    # check what types of symbols are valid and invalid

    a.define_symbol('VaLiD', 1234)
    a.define_symbol('valid3', 1234)
    a.define_symbol('VALIIIID', 1234)

    # invalid
    with pytest.raises(AssertionError):
        a.define_symbol('1234', 1234)

    # invalid
    with pytest.raises(AssertionError):
        a.define_symbol('1nvalid', 1234)

    # invalid
    with pytest.raises(AssertionError):
        a.define_symbol('invalid!', 1234)

    a.define_symbol('AnotherOne', 0x3100)

    assert a.get_symbol_location('valid') == 1234
    assert a.get_symbol_location('VALID') == 1234

    with pytest.raises(AssertionError):
        a.define_symbol('validbadlocation', -1)

    with pytest.raises(AssertionError):
        a.define_symbol('validbadlocation', 16777217)

    with pytest.raises(AssertionError):
        a.define_symbol('this is a bad label', 1232)

    # clear symbol
    a.clear_symbol('valid')
    # doing more than once should not give errors
    a.clear_symbol('valid')

    # nor should clearing ones that did not exist
    a.clear_symbol('b o g u s')

    # get symbol location

    assert a.get_symbol_location('AnotherOne') == 0x3100

    with pytest.raises(AssertionError):
        a.get_symbol_location('DoesntExist')

def test_list_file_json():

    a = ListFile()

    assert a.to_json() == '{"data": {}, "symbols": {}}'

    a.define_symbol('DataA', 0x1000)
    a.define_symbol('DataB', 0x1200)

    a.insert_data_at_symbol('DataA', '010203040506')
    a.insert_data_at_symbol('DataB', 'DEADBEEF')

    a.insert_data(0x3000, 'AAAAAAAAAAAAAAAAAAAAAAAA')
    a.insert_data(0x3500, 'AAAAAAAAAAAAAAAAAAAAAAAB')

    # dump a to json and then encode it back
    # this is done because json dumps would not correctly order the sub dictionaries sometimes
    # so instead this just compares the values of the two
    a_val = json.loads(a.to_json())
    expected_val = json.loads('{"data": {"4096": "010203040506", "4608": "DEADBEEF", "12288": "AAAAAAAAAAAAAAAAAAAAAAAA", "13568": "AAAAAAAAAAAAAAAAAAAAAAAB"}, "symbols": {"DataA": 4096, "DataB": 4608}}')

    assert a_val == expected_val

    b = ListFile()
    b.load_from_json('{"data": {"4096": "010203040506", "4608": "DEADBEEF", "12288": "AAAAAAAAAAAAAAAAAAAAAAAA", "13568": "AAAAAAAAAAAAAAAAAAAAAAAB"}, "symbols": {"DataA": 4096, "DataB": 4608}}')
    print(b.data)
    print(b.symbols)
    print(a.data)
    print(a.symbols)

    b_val = json.loads(b.to_json())

    assert b_val == expected_val

    assert a == b

    # try not equals
    b.define_symbol('DataB', 0x1201)
    assert a != b
