from ..enum.ea_mode import EAMode
from ..util.parsing import parse_assembly_parameter


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


def get_size(command: str, default_size='W') -> chr:
    """
    Gets the size of a command, or supplies the default size

    >>> get_size("MOVE.B")
    'B'

    >>> get_size("MOVE")
    'W'

    >>> get_size("MOVE", default_size='B')
    'B'

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
    return split[1]


def check_valid_command(command: str, template: str, can_take_size=True, valid_sizes='BWL') -> bool:
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

    >>> check_valid_command("MOVEA.W", "MOVEA", valid_sizes='WL')
    True

    >>> check_valid_command("MOVEA.B", "MOVEA", valid_sizes='WL')
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
        if not parts[1] in valid_sizes:
            return False  # Invalid size specifier
    else:
        return False  # More than 2 parts in the command (more than 2 periods somehow)

    return True


def ea_to_binary_post_op(ea: EAMode, size: chr) -> str:
    """
    Gets the binary (if any) of an EA Mode to append after the command itself. For example, if we were to do
    'MOVE.B #$42, D0', the immediate would need to be appended after the command: this returns the part that
    needs to be appended.

    >>> ea_to_binary_post_op(parse_assembly_parameter('#$42'), 'B')
    '0000000001000010'

    >>> ea_to_binary_post_op(parse_assembly_parameter('D0'), 'W')
    ''

    >>> ea_to_binary_post_op(parse_assembly_parameter('#$42'), 'L')
    '00000000000000000000000001000010'

    >>> ea_to_binary_post_op(parse_assembly_parameter('($242).W'), 'W')
    '0000001001000010'

    >>> ea_to_binary_post_op(parse_assembly_parameter('($242).L'), 'L')
    '00000000000000000000001001000010'

    :param ea: The effective address that needs to be converted
    :param size: The size of the operation
    :return: The binary that needs to be appended, in string form (or an empty string)
    """
    if ea.mode == EAMode.IMM:
        if size.upper() == 'L':
            return '{0:032b}'.format(ea.data)
        else:
            return '{0:016b}'.format(ea.data)

    if ea.mode == EAMode.AWA:
        return '{0:016b}'.format(ea.data)
    if ea.mode == EAMode.ALA:
        return '{0:032b}'.format(ea.data)

    return ''  # This EA doesn't have a necessary post-op
