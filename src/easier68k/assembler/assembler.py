from ..core.util.parsing import strip_comments, has_label, get_label, strip_label, get_opcode, strip_opcode, parse_literal
import sys
import types
import re
import binascii
from ..core import opcodes
from ..core.models.list_file import ListFile
# This *is* actually a necessary import due to using "reflection" style code further down
# noinspection PyUnresolvedReferences
from ..core.opcodes import *

valid_opcodes = [
    'easier68k.core.opcodes.move'
]

MAX_MEMORY_LOCATION = 16777216  # 2^24


def for_line_stripped_comments(full_text: str):
    for line_index, line in enumerate(full_text.splitlines()):
        stripped = strip_comments(line)
        if not stripped.strip():
            continue

        yield line_index + 1, stripped  # line_index + 1 because here the line indices are zero-based


<<<<<<< 262bb70bacc453cc9feeb29799d0495291e2b2f3

def parse(text: str):  # should return a list file and errors/warnings eventually
=======
def for_line_opcode_parse(full_text: str):
>>>>>>> Continue PR review and implemented some code reuse
    """
    Yields the label (if it exists), opcode, and opcode contents for every line in a file
    :param full_text: The file text to parse
    :return: Yields the label (or None), opcode, and opcode contents (returns nothing)
    """
    for line_index, stripped in for_line_stripped_comments(full_text):
        yield get_label(stripped) if has_label(stripped) else None, get_opcode(stripped), strip_opcode(stripped)


def find_labels(text: str) -> (dict, dict, list):
    """
    Finds all labels from a file
    :param text: The text to search through for labels
    :return: In order, labels (dict of label to line index + label contents), equates (dict of label to contents), and
             issues (list of message + severity)
    """
    labels = {}
    equates = {}
    issues = []

    for line_index, stripped in for_line_stripped_comments(text):
        if has_label(stripped):
            label = get_label(stripped)

            # Remove extra spaces at this point because they're no use
            # and could only have negative implications
            label_contents = strip_label(stripped).strip()

            if label in labels.keys():
                issues.append(('Label {} already declared'.format(label), 'ERROR'))
            else:
                labels[label] = (line_index, label_contents)
                if get_opcode(stripped) == 'EQU':
                    equates[label] = strip_opcode(stripped)

    return labels, equates, issues


def find_module(opcode: str):  # Note: didn't add a type specifier because I dunno how to specify module and class types
    """
    Finds the proper module and module class based on the opcode
    :param opcode: The opcode to search for
    :return: The module and class found (or (None, None) if it doesn't find any)
    """
    op_module = None
    op_class = None

    for m in valid_opcodes:
        mod = sys.modules[m]
        if mod.command_matches(opcode):
            op_module = mod
            op_class = getattr(op_module, op_module.class_name)

    return op_module, op_class


def replace_equates(contents: str, equates: dict) -> str:
    for equate in equates.items():
        contents = contents.replace(equate[0], equate[1])

    return contents


def replace_label_addresses(contents: str, label_addresses: dict) -> str:
    for label in label_addresses.items():
        contents = contents.replace(label[0], '$' + hex(label[1])[2:])

    return contents


def parse(text: str):  # should return a list file and errors/warnings eventually
    """
    Parses an assembly file and returns a list file, along with errors/warnings from the parsing process.
    :param text: The assembly file text to parse
    :return: The parsed list file
    """

    # --- PART 1: process for labels and equates ---
    labels, equates, issues = find_labels(text)

    # --- PART 2: process operations for sizing and lay out memory ---
    to_return = ListFile()
    current_memory_location = 0x00000000
    label_addresses = {}  # Stores all of the label memory locations

    for label, opcode, contents in for_line_opcode_parse(text):
        # Equates have already been processed, skip them
        # (this idea could be expanded for more preprocessor directives)
        if opcode == 'EQU':
            continue

        # Replace all substitutions in the current line with their corresponding values
        contents = replace_equates(contents, equates)

        if opcode == 'ORG':  # This will shift our current memory location, it's a special case
<<<<<<< 262bb70bacc453cc9feeb29799d0495291e2b2f3
            new_memory_location = parse_literal(contents)
            assert 0 <= new_memory_location < 16777216, 'ORG address must be between 0 and 2^24!'
=======
            parsed = parse_literal(contents)
            new_memory_location = int.from_bytes(parsed, 'big')
            assert 0 <= new_memory_location < MAX_MEMORY_LOCATION, 'ORG address must be between 0 and 2^24!'
>>>>>>> Continue PR review and implemented some code reuse
            current_memory_location = new_memory_location
            continue

        if label is not None:
            label_addresses[label] = current_memory_location
            to_return.define_symbol(label, current_memory_location)

        # TODO: Possibly cache this (and the module search) for Part 3 later so we don't have to redo introspection?
        op_module, op_class = find_module(opcode)

        # We don't know this opcode, there's no module for it
        if op_module is None:
            issues.append(('Opcode {} is not known: skipping and continuing'.format(opcode), 'ERROR'))
            continue

        length, issues = op_class.get_word_length(opcode, contents)

        current_memory_location += length * 2

    current_memory_location = 0x00000000

    # --- PART 3: actually create the list file ---
    for l, opcode, contents in for_line_opcode_parse(text):
        # Equates have already been processed, skip them
        # (this idea could be expanded for more preprocessor directives)
        if opcode == 'EQU':
            continue

        # Replace all substitutions in the current line with their corresponding values
        contents = replace_equates(contents, equates)

        # Replace all memory labels with their proper values (that's the difference in this step)
        contents = replace_label_addresses(contents, label_addresses)

        if opcode == 'ORG':  # This will shift our current memory location, it's a special case
<<<<<<< f4fbfcf933e13d5a4e22f5f86c7470c7ca7134c1
            new_memory_location = parse_literal(contents)
            assert 0 <= new_memory_location < 16777216, 'ORG address must be between 0 and 2^24!'
=======
            parsed = parse_literal(contents)
            new_memory_location = int.from_bytes(parsed, 'big')
            assert 0 <= new_memory_location < MAX_MEMORY_LOCATION, 'ORG address must be between 0 and 2^24!'
>>>>>>> Implemented PR feedback
            current_memory_location = new_memory_location
            continue

        # TODO: Possibly use a cached version?
        op_module, op_class = find_module(opcode)

        if op_module is None:
            issues.append(('Opcode {} is not known: skipping and continuing'.format(opcode), 'ERROR'))

        # We don't know this opcode, there's no module for it
        if op_module is None:
            issues.append(('Opcode {} not known, but continuing and dropping it.', 'ERROR'))
            continue

        # Get the actual constructed opcode
        data, issues = op_class.from_str(opcode, contents)

        # Write the data to the list file
        to_return.insert_data(current_memory_location, str(binascii.hexlify(data.assemble()))[2:-1])

        # Increment our memory counter
        current_memory_location += length * 2

    return to_return
