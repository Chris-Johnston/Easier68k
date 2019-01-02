# This *is* actually a necessary import due to using "reflection" style code further down
# noinspection PyUnresolvedReferences
from ..opcodes import *
from types import ModuleType
import sys

valid_opcode_classes = [
    'easier68k.core.opcodes.move.Move',
    'easier68k.core.opcodes.simhalt.Simhalt',
    'easier68k.core.opcodes.dc.DC',
    'easier68k.core.opcodes.lea.Lea',
    'easier68k.core.opcodes.trap.Trap',
    'easier68k.core.opcodes.opcode_or.Or',
    'easier68k.core.opcodes.add.Add',
    'easier68k.core.opcodes.bcc.Bra',
    'easier68k.core.opcodes.bcc.Bhi',
    'easier68k.core.opcodes.bcc.Bls',
    'easier68k.core.opcodes.bcc.Bcc',
    'easier68k.core.opcodes.bcc.Bcs',
    'easier68k.core.opcodes.bcc.Bne',
    'easier68k.core.opcodes.bcc.Beq',
    'easier68k.core.opcodes.bcc.Bvc',
    'easier68k.core.opcodes.bcc.Bvs',
    'easier68k.core.opcodes.bcc.Bpl',
    'easier68k.core.opcodes.bcc.Bmi',
    'easier68k.core.opcodes.bcc.Bge',
    'easier68k.core.opcodes.bcc.Blt',
    'easier68k.core.opcodes.bcc.Bgt',
    'easier68k.core.opcodes.bcc.Ble'
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
