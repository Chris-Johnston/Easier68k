import pytest
import json
from easier68k.core.models.list_file import ListFile
from easier68k.assembler.assembler import parse


def test_basic_test_input():
    # Test
    with open('easier68k/assembler/basic_test_input.x68') as x68:
        assembled, issues = parse(x68.read(-1))

        with open('easier68k/assembler/temp_output_file.txt', 'w') as out:  # Temporary output file for testing results
            pretty_json = json.loads(assembled.to_json())
            out.write(json.dumps(pretty_json, indent=4, sort_keys=True))
            if issues:
                out.write('\r\n----- ISSUES -----\r\n')
                for issue in issues:
                    out.write('{}: {}\r\n'.format(issue[1], issue[0]))

        assert isinstance(assembled, ListFile)
        assert assembled.starting_execution_address == 1024
        assert len(assembled.symbols) == 1
        assert assembled.symbols['magic'] == 1046
        assert len(assembled.data) == 5
        assert assembled.data['1024'] == '303cfffd'
        assert assembled.data['1028'] == '33fcabcd00aaaaaa'
        assert assembled.data['1036'] == '41f900000412'
        assert assembled.data['1042'] == 'ffffffff'
        assert assembled.data['1046'] == 'abcd'
        assert not issues
