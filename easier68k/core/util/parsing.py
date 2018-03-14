# Parsing utils
from ..enum.ea_mode import EAMode
from ..models.assembly_parameter import AssemblyParameter
from ..enum.op_size import OpSize

def from_str_util(command: str, parameters: str) -> (OpSize, list, list):
    """
    Util method for from_str
    Splits the command into both parts, gets the normalized size
    and splits the parameters

    >>> from_str_util('MOVE.B', '#123, D0')
    (<OpSize.BYTE: 1>, ['#123', 'D0'], ['MOVE', 'B'])

    >>> from_str_util('FAKEOP', '$AAAA, #123, $AAAA')
    (<OpSize.WORD: 2>, ['$AAAA', '#123', '$AAAA'], ['FAKEOP'])

    >>> from_str_util('NOPARAM.L', '')
    (<OpSize.LONG: 4>, [''], ['NOPARAM', 'L'])

    :param command: the command str
    :param parameters: the parameters str
    :return: size {str}, params {list} of str, parts - both sides of the command after split
    """
    parts = command.split('.')  # split the command by . if specified
    if len(parts) == 1:
        size = 'W'  # default size
    else:
        size = parts[1]

    # split parameters
    params = parameters.split(',')

    # strip away whitespace for the params
    for x in range(len(params)):
        params[x] = params[x].strip()

    return OpSize.parse(size), params, parts

def parse_assembly_parameter(addr: str) -> AssemblyParameter:
    """
    Parses an effective addressing mode (such as D0, (A1), #$01)
    and makes a new AssemblyParameter

    >>> parse_assembly_parameter('D')
    Traceback (most recent call last):
    ...
    AssertionError

    >>> str(parse_assembly_parameter('D3'))
    'EA Mode: EAMode.DRD, Data: 3'

    >>> str(parse_assembly_parameter('A6'))
    'EA Mode: EAMode.ARD, Data: 6'

    >>> str(parse_assembly_parameter('(A4)'))
    'EA Mode: EAMode.ARI, Data: 4'

    >>> str(parse_assembly_parameter('(A2)+'))
    'EA Mode: EAMode.ARIPI, Data: 2'

    >>> str(parse_assembly_parameter('(A2)-'))  # Invalid, can't do "post-decrement"
    Traceback (most recent call last):
    ...
    AssertionError

    >>> str(parse_assembly_parameter('($45).W'))
    'EA Mode: EAMode.AWA, Data: 69'

    >>> str(parse_assembly_parameter('(%01010111).L'))
    'EA Mode: EAMode.ALA, Data: 87'

    >>> str(parse_assembly_parameter('#$FF'))
    'EA Mode: EAMode.IMM, Data: 255'

    >>> str(parse_assembly_parameter('-(A2)'))
    'EA Mode: EAMode.ARIPD, Data: 2'
    """
    assert len(addr) >= 2

    if addr[0] == 'D':
        assert len(addr) == 2
        assert 0 <= int(addr[1]) <= 7
        return AssemblyParameter(EAMode.DRD, int(addr[1]))
    if addr[0] == 'A':
        assert len(addr) == 2
        assert 0 <= int(addr[1]) <= 7
        return AssemblyParameter(EAMode.ARD, int(addr[1]))
    if addr[0] == '(':  # ARI, ARIPI, ALA, or AWA
        # Parse the inside of the parentheses
        nested = ""
        found_paren = False

        i = 1
        while i < len(addr):
            if addr[i] == ')':
                found_paren = True
                break

            nested += addr[i]
            i += 1

        assert found_paren

        if addr[1] == 'A':  # ARI or ARIPI
            assert nested[0] == 'A'
            assert nested[1].isnumeric()
            assert 0 <= int(nested[1]) <= 7

            if i == len(addr) - 1:
                return AssemblyParameter(EAMode.ARI, int(nested[1]))

            assert addr[i + 1] == '+'
            return AssemblyParameter(EAMode.ARIPI, int(nested[1]))

        # ALA or AWA
        assert i == len(addr) - 3
        assert addr[len(addr) - 1] == 'W' or addr[len(addr) - 1] == 'L'

        return AssemblyParameter(EAMode.AWA if addr[len(addr) - 1] == 'W' else EAMode.ALA, parse_literal(nested))
    if addr[0] == '#':  # IMM
        return AssemblyParameter(EAMode.IMM, parse_literal(addr[1:]))
    if addr[0] == '-':  # ARIPD
        assert len(addr) == 5
        assert addr[1] == '('
        assert addr[2] == 'A'
        assert addr[3].isnumeric()
        assert 0 <= int(addr[3]) <= 7
        assert addr[4] == ')'

        return AssemblyParameter(EAMode.ARIPD, int(addr[3]))

    return AssemblyParameter()


def parse_literal(literal: str) -> int:
    """
    Parses a literal (aka "1234" or "$A0F" or "%1001")

    >>> parse_literal('$BA1')
    2977

    >>> parse_literal('%01010111')
    87

    >>> parse_literal('57')
    57

    >>> parse_literal('400')
    400

    :param literal: A string containing the literal to parse
    :return: The parsed literal (a bytearray type)
    """
    if literal[0] == '$':  # Parsing a hex literal
        if len(literal) % 2 == 0:
            literal = literal[0] + '0' + literal[1:]

        return int(literal[1:], 16)
    if literal[0] == '%':  # Parsing a binary literal
        assert (len(literal) - 1) % 4 == 0  # Has to be divisible by 4 to convert into hex
        hexed = hex(int(literal[1:], 2))[2:]
        if len(hexed) % 2 == 1:
            hexed = '0' + hexed

        return int(hexed, 16)

    # Integer literal

    hexed = hex(int(literal))[2:]
    if len(hexed) % 2 == 1:
        # Odd length string, add 0 to the beginning
        hexed = '0' + hexed
    return int(hexed, 16)


def strip_comments(line: str) -> str:
    """
    Removes all comments from a line (basically makes this line into the 'compiler' version)

    >>> strip_comments('label TRAP #15 * This does a thing')
    'label TRAP #15 '

    >>> strip_comments('    ORG start ;label')
    '    ORG start '

    >>> strip_comments(';    ADD D0, D1 * asdf')
    ''

    :param line: The line to strip comments from
    :return: The stripped line
    """
    to_return = ''
    for c in line:
        if c == ';' or c == '*':
            break

        to_return += c

    return to_return


def has_label(line: str) -> bool:
    """
    Returns whether or not this line has a label in it (basically if it starts with a space or not)
    :param line: The line to test
    :return: Whether the test line has a label in it

    >>> has_label('data    DC.B $A3')
    True

    >>> has_label('    BEQ test')
    False

    >>> has_label('  TRAP #15')
    False

    >>> has_label(';start EQU $400')
    False

    """
    stripped = strip_comments(line)
    if not stripped.strip():  # The line is literally empty after removing comments
        return False
    return not strip_comments(line).startswith(' ')


def get_label(line: str) -> str:
    """
    Returns the label from a line (if it has one, if not returns None)

    >>> get_label('test DC.B $0A')
    'test'

    >>> get_label(';test DC.B $0A')  # should return nothing


    >>> get_label('    BEQ test')  # should return nothing


    :param line: The line to get the label from
    :return: The label in the line
    """

    if not has_label(line):
        return None

    stripped = strip_comments(line)

    label = ''

    for c in stripped:
        if c == ' ':
            break

        label += c

    return label


def strip_label(line: str) -> str:
    """
    Strips the label from a line, isolating the rest of the line
    (side effect: also strips comments)

    >>> strip_label('ORG start')
    'start'

    >>> strip_label('RTS ;comm')
    ''

    >>> strip_label(';all commented')
    ''

    >>> strip_label('MOVE D0, D1 * Moves D0 into D1')
    'D0, D1 '

    :param line: The line to strip the label from
    :return: The stripped line
    """

    stripped = strip_comments(line)
    if not stripped.strip():  # This line is literally empty after removing comments
        return ''

    to_return = ''
    found_space = False
    found_next = False

    for c in stripped:
        if c == ' ' and not found_space:
            found_space = True
            continue

        if c != ' ' and found_space and not found_next:
            found_next = True

        if found_next:
            to_return += c

    return to_return


def get_opcode(line: str) -> str:
    """
    Gets the opcode out of a line (with or without label)

    >>> get_opcode('start EQU $400')
    'EQU'

    >>> get_opcode('    MOVE.B D0, D1')
    'MOVE.B'

    >>> get_opcode('; start EQU $400')
    ''

    :param line: The line to get the opcode from
    :return: The opcode found in said line
    """

    stripped_comm = strip_comments(line)
    if not stripped_comm.strip():
        return ''

    if has_label(stripped_comm):
        stripped = strip_label(stripped_comm).strip()
    else:
        stripped = stripped_comm.strip()

    opcode = ''

    for c in stripped:
        if c == ' ':
            break

        opcode += c

    return opcode.upper()


def strip_opcode(line: str) -> str:
    """
    Strips the opcode from a line

    >>> strip_opcode('start EQU $400')
    '$400'

    >>> strip_opcode('    MOVE.B D0, D1')
    'D0, D1'

    >>> strip_opcode('    RTS')
    ''

    >>> strip_opcode('start EQU $400 ; comments!')
    '$400'

    :param line: The line to strip the opcode from
    :return: The line with the opcode stripped (as well as comments and labels)
    """

    stripped_comm = strip_comments(line)
    if not stripped_comm.strip():
        return ''

    if has_label(stripped_comm):
        stripped = strip_label(stripped_comm).strip()
    else:
        stripped = stripped_comm.strip()

    # We're now down to just the opcode + parameters, time to strip the opcode
    post_op = ''
    found_space = False
    found_next = False

    for c in stripped:
        if c == ' ' and not found_space:
            found_space = True
            continue

        if c != ' ' and not found_next and found_space:
            found_next = True

        if found_next:
            post_op += c

    return post_op


