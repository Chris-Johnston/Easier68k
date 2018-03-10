"""
>>> str(Move.from_str('MOVE.B', '-(A0), D1'))
'Move command: Size B, src Mode: 4, Data: 0, dest Mode: 0, Data: 1'

>>> str(Move.from_str('MOVE.L', 'D3, (A0)'))
'Move command: Size L, src Mode: 0, Data: 3, dest Mode: 2, Data: 0'

>>> Move.from_str('MOVE.W', 'D3, A3')[1]
[('Invalid addressing mode', 'ERROR')]
"""
from ...core.enum.ea_mode import EAMode
from ...core.enum.op_size import MoveSize
from ...core.enum.ea_mode_bin import EAModeBinary
from ...simulator.m68k import M68K
from ...core.opcodes.opcode import Opcode
from ...core.util.parsing import split_bits
from ...core.enum.ea_mode_bin import EAModeBinary


class Move(Opcode):
    # Allowed values: nothing, or some combination of B, W, and L (for byte, word, and long)
    # For example, MOVE would have 'BWL' because it can operate on any size of data, while MOVEA would have 'WL' because
    # it can't operate on byte-sized data
    allowed_sizes = 'BWL'
    
    # same as above, but for dissassembly
    allowed_sizes_binary = [MoveSize.parse(x) for x in allowed_sizes]

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a MOVE command from memory.

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        """
        valid, issues = Move.is_valid(command, parameters)
        if not valid:
            return None, issues
        # We can forego asserts in here because we've now confirmed this is valid assembly code

        parts = command.split('.')  # Split the command by period to get the size of the command
        if len(parts) == 1:  # Use the default size
            size = 'W'
        else:
            size = parts[1].upper()

        # Split the parameters into EA modes
        params = parameters.split(',')

        src = EAMode.parse_ea(params[0].strip())
        dest = EAMode.parse_ea(params[1].strip())

        return cls(src, dest, size)

    @classmethod
    def from_binary(cls, data: bytearray):
        """
        This has a non-move opcode
        >>> Move.from_binary(b'\x5E\x01')
        (None, 0)
        
        MOVE.B D1,D7
        >>> op, used = Move.from_binary(b'\x1E\x01')
        
        >>> str(op.src)
        'Mode: 0, Data: 1'
        
        >>> str(op.dest)
        'Mode: 0, Data: 7'
        
        >>> used
        1
        
        
        MOVE.L A4,(A7)
        >>> op, used = Move.from_binary(b'\x2E\x8C')
        
        >>> str(op.src)
        'Mode: 1, Data: 4'
        
        >>> str(op.dest)
        'Mode: 2, Data: 7'
        
        >>> used
        1

        Parses some raw data into an instance of the opcode class
        :param data: The data used to convert into an opcode instance
        :return: The constructed instance or none if there was an error and
            the amount of data in words that was used (e.g. extra for immediate
            data) or 0 for not a match
        """
        assert len(data) >= 2, 'opcode size is at least 1 word'
        wordsUsed = 1
        
        # 'big' endian byte order
        first_word = int.from_bytes(data[0:2], 'big')
        
        [opcode,
        size,
        destination_register,
        destination_mode,
        source_mode,
        source_register] = split_bits(first_word, [2, 2, 3, 3, 3, 3])
        
        # check opcode
        if opcode != 0b00:
            return (None, 0)
        
        # check size
        if not size in Move.allowed_sizes_binary:
            return (None, 0)
        
        size_char = MoveSize.parse_binary(size)
        
        
        
        # check source mode
        if not source_mode in EAModeBinary.VALID_SRC_EA_MODES:
            return (None, 0)
        
        source_data = source_register
        # check source register
        if source_mode == 0b111:
            if not source_register in EAModeBinary.VALID_SRC_EA_111_REGISTERS:
                return (None, 0)
                
            if source_register == EAModeBinary.REGISTER_AWA:
                source_data =  int.from_bytes(data[wordsUsed], 'big')
                wordsUsed += 1
                
            if source_register == EAModeBinary.REGISTER_ALA:
                source_data =  int.from_bytes(data[wordsUsed:wordsUsed+2], 'big')
                wordsUsed += 2
                
            if source_register == EAModeBinary.REGISTER_ALA:
                if size_char in 'BW':
                    source_data =  int.from_bytes(data[wordsUsed], 'big')
                    wordsUsed += 1
                else: #must be L
                    source_data =  int.from_bytes(data[wordsUsed:wordsUsed+2], 'big')
                    wordsUsed += 2
        
        
        
        # check destination mode
        if not destination_mode in EAModeBinary.VALID_DEST_EA_MODES:
            return (None, 0)
        
        destination_data = destination_register
        # check destination register
        if destination_mode == 0b111:
            if not destination_register in EAModeBinary.VALID_DEST_EA_111_REGISTERS:
                return (None, 0)
                
            if destination_register == EAModeBinary.REGISTER_AWA:
                destination_data =  int.from_bytes(data[wordsUsed], 'big')
                wordsUsed += 1
                
            if destination_register == EAModeBinary.REGISTER_ALA:
                destination_data =  int.from_bytes(data[wordsUsed:wordsUsed+2], 'big')
                wordsUsed += 2
        
        
        src_EA = EAMode(source_mode, source_data)
        dest_EA = EAMode(destination_mode, destination_data)
        return (cls(src_EA, dest_EA, size_char), 1)
        

    def __init__(self, src: EAMode, dest: EAMode, size='W'):
        # Check that the src is of the proper type (for example, can't move from an address register for a move command)
        assert src.mode != EAMode.ARD  # Only invalid src is address register direct
        self.src = src

        # Check that the destination is of a proper type
        assert dest.mode != EAMode.ARD and dest.mode != EAMode.IMM  # Can't take address register direct or immediates
        self.dest = dest

        # Check that this is a valid size (for example, 'MOVEA.B' is not a valid command)
        assert size.upper() in Move.allowed_sizes
        self.size = size

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """
        # Create a binary string to append to, which we'll convert to hex at the end
        tr = '00'  # Opcode
        tr += '{0:02d}'.format(MoveSize.parse(self.size))  # Size bits
        tr += EAModeBinary.parse_from_ea_mode_xnfirst(self.dest)  # Destination first
        tr += EAModeBinary.parse_from_ea_mode_mfirst(self.src)  # Source second

        to_return = bytearray.fromhex(hex(int(tr, 2))[2:])  # Convert to a bytearray
        return to_return

    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator: The simulator to execute the command on
        :return: Nothing
        """
        pass

    def __str__(self):
        # Makes this a bit easier to read in doctest output
        return 'Move command: Size {}, src {}, dest {}'.format(self.size, self.src, self.dest)

    @staticmethod
    def is_valid(command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        >>> Move.is_valid('MOVE.B', 'D0, D1')[0]
        True

        >>> Move.is_valid('MOVE.W', 'D0')[0]
        False

        >>> Move.is_valid('MOVE.G', 'D0, D1')[0]
        False

        >>> Move.is_valid('MOVE.L', 'D0, A2')[0]
        False

        >>> Move.is_valid('MOV.L', 'D0, D1')[0]
        False

        >>> Move.is_valid('MOVE.', 'D0, D1')[0]
        False

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        issues = []
        try:
            parts = command.split('.')  # Split the command by period to get the size of the command
            assert len(parts) <= 2, 'Unknown error (more than 1 period in command)'  # If we have more than 2 parts something is seriously wrong
            assert parts[0].upper() == 'MOVE', 'Incorrect command passed in'
            if len(parts) != 1:  # Has a size specifier
                assert len(parts[1]) == 1, 'Size specifier must be 1 character'
                assert parts[1] in Move.allowed_sizes, "Size {} isn't allowed for command {}".format(parts[1], command[0])

            # Split the parameters into EA modes
            params = parameters.split(',')
            assert len(params) == 2, 'Must have two parameters'

            src = EAMode.parse_ea(params[0].strip())  # Parse the source and make sure it parsed right
            assert src.mode > EAMode.ERR, 'Error parsing src'  # -1 means error

            dest = EAMode.parse_ea(params[1].strip())
            assert dest.mode > EAMode.ERR, 'Error parsing dest'  # -1 means error

            assert src.mode != EAMode.ARD, 'Invalid addressing mode'  # Only invalid src is address register direct
            assert dest.mode != EAMode.ARD and dest.mode != EAMode.IMM, 'Invalid addressing mode'

            return True, issues
        except AssertionError as e:
            issues.append((e.args[0], 'ERROR'))
            return False, issues

    @staticmethod
    def get_word_length(command: str, parameters: str) -> (int, list):
        """
        >>> Move.get_word_length('MOVE', 'D0, D1')
        (1, [])

        >>> Move.get_word_length('MOVE.L', '#$90, D3')
        (3, [])

        >>> Move.get_word_length('MOVE.W', '#$90, D3')
        (2, [])

        >>> Move.get_word_length('MOVE.W', '($AAAA).L, D7')
        (3, [])

        >>> Move.get_word_length('MOVE.W', 'D0, ($BBBB).L')
        (3, [])

        >>> Move.get_word_length('MOVE.W', '($AAAA).L, ($BBBB).L')
        (5, [])

        >>> Move.get_word_length('MOVE.W', '#$AAAA, ($BBBB).L')
        (4, [])


        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words, as well as a list of warnings or errors encountered
        """
        valid, issues = Move.is_valid(command, parameters)
        if not valid:
            return 0, issues
        # We can forego asserts in here because we've now confirmed this is valid assembly code

        issues = []  # Set up our issues list (warnings + errors)
        parts = command.split('.')  # Split the command by period to get the size of the command
        if len(parts) == 1:  # Use the default size
            size = 'W'
        else:
            size = parts[1]

        # Split the parameters into EA modes
        params = parameters.split(',')

        src = EAMode.parse_ea(params[0].strip())  # Parse the source and make sure it parsed right
        dest = EAMode.parse_ea(params[1].strip())

        length = 1  # Always 1 word not counting additions to end

        if src.mode == EAMode.IMM:  # If we're moving an immediate we have to append the value afterwards
            if size == 'L':
                length += 2  # Longs are 2 words long
            else:
                length += 1  # This is a word or byte, so only 1 word

        if src.mode == EAMode.AWA:  # Appends a word
            length += 1

        if src.mode == EAMode.ALA:  # Appends a long, so 2 words
            length += 2

        if dest.mode == EAMode.AWA:  # Appends a word
            length += 1

        if dest.mode == EAMode.ALA:  # Appends a long, so 2 words
            length += 2

        return length, issues
