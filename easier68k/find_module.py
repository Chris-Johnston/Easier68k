# This *is* actually a necessary import due to using "reflection" style code further down
# noinspection PyUnresolvedReferences
from .opcodes import *
from types import ModuleType
import sys

valid_opcode_classes = [
    'easier68k.opcodes.move.Move',
    'easier68k.opcodes.simhalt.Simhalt',
    'easier68k.opcodes.dc.DC',
    'easier68k.opcodes.lea.Lea',
    'easier68k.opcodes.trap.Trap',
    'easier68k.opcodes.opcode_or.Or',
    'easier68k.opcodes.add.Add',
    'easier68k.opcodes.bcc.Bra',
    'easier68k.opcodes.bcc.Bhi',
    'easier68k.opcodes.bcc.Bls',
    'easier68k.opcodes.bcc.Bcc',
    'easier68k.opcodes.bcc.Bcs',
    'easier68k.opcodes.bcc.Bne',
    'easier68k.opcodes.bcc.Beq',
    'easier68k.opcodes.bcc.Bvc',
    'easier68k.opcodes.bcc.Bvs',
    'easier68k.opcodes.bcc.Bpl',
    'easier68k.opcodes.bcc.Bmi',
    'easier68k.opcodes.bcc.Bge',
    'easier68k.opcodes.bcc.Blt',
    'easier68k.opcodes.bcc.Bgt',
    'easier68k.opcodes.bcc.Ble'
]

valid_opcodes = [
    x.split('.')[-1].upper() for x in valid_opcode_classes
]


def find_opcode_cls(opcode: str) -> type:  # classes are of type "type" Really python?
    """
    Finds the proper module and module class based on the opcode
    :param opcode: The opcode to search for
    :return: The module and class found (or (None, None) if it doesn't find any)
    """
    for m in valid_opcode_classes:
        split = m.split('.')
        mod_name = '.'.join(split[:-1])  # Trims the class name (the last part after the period)
        mod = sys.modules[mod_name]
        cls = getattr(mod, split[-1])
        if cls.command_matches(opcode):
            return cls

    return None
