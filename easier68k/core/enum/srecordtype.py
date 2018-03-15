"""
Type used by the S record files
"""
from enum import Enum

# forward definition
class SRecordType(Enum):
    pass

class SRecordType(Enum):
    S0 = 0
    S1 = 1
    S2 = 2
    S3 = 3
    S4 = 4
    S5 = 5
    S6 = 6
    S7 = 7
    S8 = 8
    S9 = 9

    @staticmethod
    def parse(record_str: str) -> SRecordType:
        assert record_str[0] is 'S'
        num = int(record_str[1])
        return SRecordType(num)