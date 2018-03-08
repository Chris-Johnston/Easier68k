# Parsing utils


def parse_literal(literal: str):
    """
    Parses a literal (aka "1234" or "$A0F" or "%1001")

    >>> parse_literal('$BA1')
    bytearray(b'\\x0b\\xa1')

    >>> parse_literal('%01010111')
    bytearray(b'W')

    >>> parse_literal('57')
    bytearray(b'9')

    >>> parse_literal('400')
    bytearray(b'\\x01\\x90')

    :param literal: A string containing the literal to parse
    :return: The parsed literal (a bytearray type)
    """
    if literal[0] == '$':  # Parsing a hex literal
        if len(literal) % 2 == 0:
            literal = literal[0] + '0' + literal[1:]

        return bytearray.fromhex(literal[1:])
    if literal[0] == '%':  # Parsing a binary literal
        assert (len(literal) - 1) % 4 == 0  # Has to be divisible by 4 to convert into hex
        hexed = hex(int(literal[1:], 2))[2:]
        if len(hexed) % 2 == 1:
            hexed = '0' + hexed

        return bytearray.fromhex(hexed)

    # Integer literal
    hexed = hex(int(literal))[2:]
    if len(hexed) % 2 == 1:
        # Odd length string, add 0 to the beginning
        hexed = '0' + hexed
    return bytearray.fromhex(hexed)


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

    return opcode


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
