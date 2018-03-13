import pytest
import json
from easier68k.assembler.assembler import parse


def test_basic_test_input():
    # Test
    with open('easier68k/assembler/basic_test_input.x68') as x68:
        assembled, issues = parse(x68.read(-1))
        with open('easier68k/assembler/temp_output_file.txt', 'w') as out:  # Temporary output file for testing results
            pretty_json = json.loads(assembled.to_json())
            out.write(json.dumps(pretty_json, indent=4))
            out.write('\r\n----- ISSUES -----')
            for issue in issues:
                out.write('{}: {}\r\n'.format(issue[1], issue[0]))
