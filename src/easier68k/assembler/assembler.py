from ..core.util.parsing import strip_comments, has_label, get_label, strip_label, get_opcode, strip_opcode, parse_literal
import binascii
import sys
from ..core import opcodes
from ..core.opcodes import *


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

    line_index = 0
    for line in text.splitlines():
        line_index += 1
        stripped = strip_comments(line)
        if not stripped.strip():
            continue

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
                    equates[label] = parse_literal(strip_opcode(stripped))

    # --- PART 2: process operations for sizing and lay out memory ---

    for m in opcodes.__all__:
        module = sys.modules['easier68k.core.opcodes.{}'.format(m)]
        # print(module)
