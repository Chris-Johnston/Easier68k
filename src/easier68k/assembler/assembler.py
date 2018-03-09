from ..core.util.parsing import strip_comments, has_label, get_label, strip_label, get_opcode, strip_opcode, parse_literal
import sys
import types
import re
import binascii
from ..core import opcodes
# This *is* actually a necessary import due to using "reflection" style code further down
# noinspection PyUnresolvedReferences
from ..core.opcodes import *


def for_line_stripped_comments(full_text: str):
    line_index = 0
    for line in full_text.splitlines():
        line_index += 1
        stripped = strip_comments(line)
        if not stripped.strip():
            continue

        yield line_index, stripped

def parse(text: str):  # should return a list file and errors/warnings eventually
    """
    Parses an assembly file and returns a list file, along with errors/warnings from the parsing process.
    :param text: The assembly file text to parse
    :return: The parsed list file
    """

    # --- PART 1: process for labels and equates ---

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

    # --- PART 2: process operations for sizing and lay out memory ---

    current_memory_location = 0x00000000
    label_addresses = {}  # Stores all of the label memory locations

    out_test = open('temp_output_file.txt', 'w')

    for m in opcodes.__all__:
        module = sys.modules['easier68k.core.opcodes.{}'.format(m)]

    for line_index, stripped in for_line_stripped_comments(text):
        no_label = strip_label(stripped)
        opcode = get_opcode(stripped).upper()

        # Equates have already been processed, skip them
        # (this idea could be expanded for more preprocessor directives)
        if opcode == 'EQU':
            continue

        contents = strip_opcode(stripped)
        for equate in equates.items():
            contents = contents.replace(equate[0], equate[1])

        if opcode == 'ORG':  # This will shift our current memory location, it's a special case
            parsed = parse_literal(contents)
            # TODO: Max/min memory location?
            current_memory_location = int.from_bytes(parsed, 'big')
            out_test.write(hex(current_memory_location) + " | ORGed at " + str(parsed) + "\r\n")
            continue

        if opcode.lower() not in opcodes.__all__:
            issues.append(('Opcode {} not known, but continuing and dropping it.', 'ERROR'))
            continue

        op_module = sys.modules['easier68k.core.opcodes.{}'.format(opcode.lower())]
        op_class = getattr(op_module, opcode.capitalize())
        length, issues = op_class.get_word_length(opcode, contents)

        current_memory_location += length * 2
