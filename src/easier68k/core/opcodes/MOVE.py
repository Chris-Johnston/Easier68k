from ...core.enum.ea_mode import EAMode
from ...core.enum.op_size import BigSSize
from ...core.enum.ea_mode_bin import EAModeBinary
from ...simulator.m68k import M68K
import binascii

# Allowed values: nothing, or some combination of B, W, and L (for byte, word, and long)
# For example, MOVE would have 'BWL' because it can operate on any size of data, while MOVEA would have 'WL' because
# it can't operate on byte-sized data
allowed_sizes = 'BWL'


class MOVE:
    # Include parameters here
    def __init__(self, src: EAMode, dest: EAMode, size='B'):
        assert src.mode != EAMode.ARD  # Only invalid src is address register direct
        self.src = src

        assert dest.mode != EAMode.ARD and dest.mode != EAMode.IMM  # Can't take address register direct or immediates
        self.dest = dest

        assert size in allowed_sizes
        self.size = size

    def assemble(self) -> bytearray:
        tr = ''
        tr += '00'
        tr += '{0:02d}'.format(BigSSize.parse(self.size))
        tr += EAModeBinary.parse_from_ea_mode_xnfirst(self.dest)
        tr += EAModeBinary.parse_from_ea_mode_mfirst(self.src)

        to_return = bytearray.fromhex(hex(int(tr, 2))[2:])
        print(binascii.hexlify(to_return))

    def execute(self, simulator: M68K):
        pass

    def __str__(self):
        return 'Move command: Size {}, src {}, dest {}'.format(self.size, self.src, self.dest)


def get_byte_length(command: str, parameters: str) -> (int, list):
    """
    >>> get_byte_length('MOVE', 'D0, D1')
    (2, [])

    >>> get_byte_length('MOVE.L', '#$90, D3')
    (6, [])

    >>> get_byte_length('MOVE.W', '#$90, D3')
    (4, [])

    >>> get_byte_length('MOVE.W', '($AAAA).L, D7')
    (6, [])

    Gets what the end length of this command will be in memory
    :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
    :param parameters: The parameters after the command
    :return: The length of the bytes in memory, as well as a list of warnings or errors encountered
    """

    issues = []
    parts = command.split('.')
    assert len(parts) <= 2
    if len(parts) == 1:
        size = 'B'
    else:
        assert parts[1] in allowed_sizes
        size = parts[1]

    # Split the parameters into EA modes
    params = parameters.split(',')
    if len(params) != 2:
        issues.append(('Invalid syntax (missing a parameter)', 'ERROR'))
        return 0, issues

    try:
        src = EAMode.parse_ea(params[0].strip())
        assert src.mode > EAMode.ERR  # -1 means error
    except AssertionError:
        issues.append(('Error parsing source', 'ERROR'))
        return 0, issues

    try:
        dest = EAMode.parse_ea(params[1].strip())
        assert dest.mode > EAMode.ERR  # -1 means error
    except AssertionError:
        issues.append(('Error parsing destination', 'ERROR'))
        return 0, issues

    length = 2  # Always 2 bytes not counting additions to end

    assert src.mode != EAMode.ARD  # Only invalid src is address register direct
    assert dest.mode != EAMode.ARD and dest.mode != EAMode.IMM  # Can't take address register direct or immediates

    if src.mode == EAMode.IMM:
        if size == 'L':
            length += 4
        else:
            length += 2

    if src.mode == EAMode.AWA:
        length += 2

    if src.mode == EAMode.ALA:
        length += 4

    return length, issues


def assemble(command: str, parameters: str) -> (MOVE, list):
    """
    Assembles the given parameters into binary suitable for writing to memory

    >>> str(assemble('MOVE.B', '-(A0), D1')[0])
    'Move command: Size B, src Mode: 4, Data: 0, dest Mode: 0, Data: 1'

    :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
    :param parameters: The parameters after the command
    :return: The bytes to write, as well as a list of warnings or errors encountered
    """
    issues = []
    parts = command.split('.')
    assert len(parts) <= 2
    if len(parts) == 1:
        size = 'B'
    else:
        assert parts[1] in allowed_sizes
        size = parts[1]

    # Split the parameters into EA modes
    params = parameters.split(',')
    if len(params) != 2:
        issues.append(('Invalid syntax (missing a parameter)', 'ERROR'))
        return 0, issues

    try:
        src = EAMode.parse_ea(params[0].strip())
        assert src.mode > EAMode.ERR  # -1 means error
    except AssertionError:
        issues.append(('Error parsing source', 'ERROR'))
        return 0, issues

    try:
        dest = EAMode.parse_ea(params[1].strip())
        assert dest.mode > EAMode.ERR  # -1 means error
    except AssertionError:
        issues.append(('Error parsing destination', 'ERROR'))
        return 0, issues

    return MOVE(src, dest, size), issues


