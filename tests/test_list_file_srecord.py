"""
Tests for loading s records
"""

import pytest
import json
import os.path

from easier68k import ListFile

file_path = os.path.join(os.path.dirname(__file__), 'test.S68')

example = '''{"data": {"12288": "0000000100000002000000030000000400000005000000060000000700000008", "12320": "000000090000000A0000000B0000000C0000000D0000000E0000000F00000010", "12544": "0000000100000002000000030000000400000005000000060000000700000008", "12576": "000000090000000A0000000B0000000C0000000D0000000E0000000F00000010", "12800": "00000000000000000000000000000000", "4096": "78007A007C007E006000002278005846BC7C00106C000006600000127C005845", "4128": "BA7C00106C00004A60000002B87C001049F83000D8C43405C4FC0004D8C24BF8", "4160": "3100DAC6343C007BC4FC0004DAFC00AF4DF83200DCC63405C4FC0004DCC22414", "4192": "2615C7C22416D6822C835844584760BCFFFF", "4208": "FFFF"}, "startingExecutionAddress": 4096, "symbols": {}}'''

def test_srecord():
    """
    Test the S record file loading
    :return:
    """
    lf = ListFile()

    lf.read_s_record_filename(file_path)

    output = ListFile()
    output.load_from_json(example)

    assert lf == output