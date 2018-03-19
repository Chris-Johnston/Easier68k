"""
TrapTask
Represents the different types of tasks that are done with the TRAP opcode

Not all functions of TRAP are supported
"""

from enum import IntEnum

class TrapTask(IntEnum):

    # Read a null terminated string from the input
    # store at (A1), length returned in D1.W (max 80)
    ReadNullTermString = 2

    # Displays signed number in D1.L in decimal
    DisplaySignedNumber = 3

    # Read a number from the keyboard into D1.L
    ReadNumberFromKeyboard = 4

    # Read a single character from the keyboard into D1.B
    ReadSingleCharacterFromKeyboard = 5

    # Display single character in D1.B
    DisplaySingleCharacter = 6

    # Terminate the program, same as SIMHALT
    Terminate = 9

    # Display the null-terminated string at (A1) with CRLF
    DisplayNullTermStringWithCRLF = 13

    # Display the null terminated string at (A1) (without CRLF)
    DisplayNullTermString = 14

    # Display the null terminated string at (A1) without CR, LF then reads a number into D1.L
    DisplayNullTermStringAndReadNumberFromKeyboard = 18
