from src.easier68k.core.util.parsing import strip_comments, has_label, get_label, strip_label, get_opcode, strip_opcode, parse_literal
import binascii


def parse(text: str):  # should return a ListFile and errors/warnings eventually
    # --- PART 1: process for labels and equates ---

    labels = {}
    equates = {}

    line_index = 0
    for line in text.splitlines():
        line_index += 1
        stripped = strip_comments(line)
        if not stripped.strip():
            continue

        print(strip_comments(line))

        if has_label(stripped):
            label = get_label(stripped)

            # Remove extra spaces at this point because they're no use
            # and could only have negative implications
            label_contents = strip_label(stripped).strip()

            if label in labels.keys():
                print('ERROR: label already declared')
            else:
                labels[label] = (line_index, label_contents)
                if get_opcode(stripped) == 'EQU':
                    equates[label] = parse_literal(strip_opcode(stripped))

    print('----- LABELS -----')
    for l in labels.items():
        print('Label {} at line {}: {}'.format(l[0], l[1][0], l[1][1]))

    print('----- EQUATES -----')
    for e in equates.items():
        print('{} = {}'.format(e[0], binascii.hexlify(e[1])))


# Test
f = open('temptests/temptest.txt')
parse(f.read(-1))
