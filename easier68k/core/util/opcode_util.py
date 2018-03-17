from ..enum.ea_mode import EAMode
from ..util.parsing import parse_assembly_parameter, from_str_util
from ..enum.op_size import OpSize


def command_matches(command: str, template: str) -> bool:
    """

    >>> command_matches("MOVE.B", "MOVE")
    True

    >>> command_matches("MOVE", "MOVE")
    True

    >>> command_matches("MOV", "MOVE")
    False

    >>> command_matches("MOV.B", "MOVE")
    False

    Handles the typical checking of a command string (like 'MOVE.B', 'LEA', etc.).
    NOTE: this will match some error conditions, this just does the broadest possible checks. The main one is that this
    doesn't check for more than 1 period (MOVE.B.W, for example) or check for valid sizes/lack of sizes. The assumption
    is that this will be handled in the actual parsing methods for proper error handling.
    :param command: The command string to parse
    :param template: The template to check with
    :return: Whether the command matches
    """
    split = command.split('.')

    # There's no size argument here
    if len(split) == 1:
        return command == template

    # There's a size argument
    return split[0] == template


def get_size(command: str, default_size=OpSize.WORD) -> OpSize:
    """
    Gets the size of a command, or supplies the default size

    >>> get_size("MOVE.B")
    <OpSize.BYTE: 1>

    >>> get_size("MOVE")
    <OpSize.WORD: 2>

    >>> get_size("MOVE", default_size=OpSize.BYTE)
    <OpSize.BYTE: 1>

    :param command: The command string to parse
    :param default_size: The default size if no size is found
    :return: The size of the command
    """
    split = command.split('.')
    assert len(split) > 0
    if len(split) == 1:
        return default_size

    assert len(split) == 2
    assert len(split[1]) == 1
    return OpSize.parse(split[1])


def check_valid_command(command: str, template: str, can_take_size=True, valid_sizes=[OpSize.LONG, OpSize.WORD, OpSize.BYTE]) -> bool:
    """
    Checks whether this command is valid

    >>> check_valid_command("MOVE.B", "MOVE")
    True

    >>> check_valid_command("MOVE", "MOVE")
    True

    >>> check_valid_command("MOV", "MOVE")
    False

    >>> check_valid_command("LEA", "LEA", can_take_size=False)
    True

    >>> check_valid_command("LEA.B", "LEA", can_take_size=False)
    False

    >>> check_valid_command("MOVEA.W", "MOVEA", valid_sizes=[OpSize.WORD, OpSize.LONG])
    True

    >>> check_valid_command("MOVEA.B", "MOVEA", valid_sizes=[OpSize.WORD, OpSize.LONG])
    False

    :param command: The command to check
    :param template: The type of command we're checking for (like 'MOVE', 'LEA', etc.)
    :param can_take_size: Whether this command takes a size argument or not
    :return: Whether this command is valid or not
    """
    parts = command.split('.')
    if len(parts) == 0:
        return False  # There's nothing here?
    if not can_take_size and len(parts) > 1:
        return False  # Can't take a size but has a size specified
    if len(parts) == 1:
        if command != template:
            return False  # Command doesn't match
    elif len(parts) == 2:
        if parts[0] != template:
            return False  # Command doesn't match
        if len(parts[1]) != 1:
            return False  # Size not 1 character
        if not OpSize.parse(parts[1]) in valid_sizes:
            return False  # Invalid size specifier
    else:
        return False  # More than 2 parts in the command (more than 2 periods somehow)

    return True


def ea_to_binary_post_op(ea: EAMode, size: OpSize) -> str:
    """
    Gets the binary (if any) of an EA Mode to append after the command itself. For example, if we were to do
    'MOVE.B #$42, D0', the immediate would need to be appended after the command: this returns the part that
    needs to be appended.

    >>> ea_to_binary_post_op(parse_assembly_parameter('#$42'), OpSize.BYTE)
    '0000000001000010'

    >>> ea_to_binary_post_op(parse_assembly_parameter('D0'), OpSize.WORD)
    ''

    >>> ea_to_binary_post_op(parse_assembly_parameter('#$42'), OpSize.LONG)
    '00000000000000000000000001000010'

    >>> ea_to_binary_post_op(parse_assembly_parameter('($242).W'), OpSize.WORD)
    '0000001001000010'

    >>> ea_to_binary_post_op(parse_assembly_parameter('($242).L'), OpSize.LONG)
    '00000000000000000000001001000010'

    :param ea: The effective address that needs to be converted
    :param size: The size of the operation
    :return: The binary that needs to be appended, in string form (or an empty string)
    """
    if ea.mode == EAMode.IMM:
        if size is OpSize.LONG:
            return '{0:032b}'.format(ea.data)
        else:
            return '{0:016b}'.format(ea.data)

    if ea.mode == EAMode.AWA:
        return '{0:016b}'.format(ea.data)
    if ea.mode == EAMode.ALA:
        return '{0:032b}'.format(ea.data)

    return ''  # This EA doesn't have a necessary post-op


def two_param_is_valid(command: str, parameters: str, opcode: str, valid_sizes=[OpSize.LONG, OpSize.WORD, OpSize.BYTE],
                       default_size=OpSize.WORD, param1_invalid_modes=[], param2_invalid_modes=[]) -> (bool, list):
    """
    Tests whether the given command is valid

    :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
    :param parameters: The parameters after the command (such as the source and destination of a move)
    :param opcode: The opcode to check for ('MOVE', 'LEA', etc.)
    :param valid_sizes: valid sizes of the command (empty list or None for no size)
    :param default_size: the default size for the command (can be None if it doesn't take a command)
    :param param1_invalid_modes: invalid modes for the first parameter
    :param param2_invalid_modes: invalid modes for the second parameter
    :return: Whether the given command is valid and a list of issues/warnings encountered
    """
    issues = []
    try:
        size, params, parts = from_str_util(command, parameters)

        # If we have more than 2 parts something is seriously wrong
        assert len(parts) <= 2, 'Unknown error (more than 1 period in command)'
        assert parts[0].upper() == opcode.upper(), "Command doesn't match template {}".format(opcode)
        # Size check
        if valid_sizes is not None and len(valid_sizes) > 0:
            if not size:
                # If size is null but we had a size parameter, it was an invalid size
                assert len(parts) == 1, 'Invalid size parameter'
                size = default_size
            assert size in valid_sizes, 'Size {} is not a valid size'.format(size)
        else:
            assert len(parts) == 1, "Can't specify a size for command {}".format(opcode)

        assert len(params) == 2, 'Opcode {} must have two parameters'.format(opcode)

        param1 = parse_assembly_parameter(params[0])
        param2 = parse_assembly_parameter(params[1])

        assert param1.mode not in param1_invalid_modes, 'Invalid addressing mode'
        assert param2.mode not in param2_invalid_modes, 'Invalid addressing mode'

    except AssertionError as e:
        issues.append((e.args[0], 'ERROR'))
        return False, issues

    return True, issues


def two_param_from_str(command: str, parameters: str, opcode_cls, default_size=OpSize.WORD):
    """
    Parses a command from text. Note that this assumes that is_valid has already been run and was successful.

    :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
    :param parameters: The parameters after the command (such as the source and destination of a move)
    :param opcode_cls: The class of opcode we're parsing to
    :param opcode: The opcode template (like 'MOVE', 'LEA', etc.)
    :param default_size: The default size if no size is specified, or None if this is an unsized opcode
    :return: The parsed command
    """
    size, params, parts = from_str_util(command, parameters)

    if default_size and not size:
        size = default_size
    elif not default_size:
        size = None

    param1 = parse_assembly_parameter(params[0].strip())
    param2 = parse_assembly_parameter(params[1].strip())

    if size:
        return opcode_cls(param1, param2, size)
    else:
        return opcode_cls(param1, param2)

