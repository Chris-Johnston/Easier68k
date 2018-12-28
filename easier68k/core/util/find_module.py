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
    'easier68k.core.opcodes.Bcc.BRA',
    'easier68k.core.opcodes.Bcc.BHI',
    'easier68k.core.opcodes.Bcc.BLS',
    'easier68k.core.opcodes.Bcc.BCC',
    'easier68k.core.opcodes.Bcc.BCS',
    'easier68k.core.opcodes.Bcc.BNE',
    'easier68k.core.opcodes.Bcc.BEQ',
    'easier68k.core.opcodes.Bcc.BVC',
    'easier68k.core.opcodes.Bcc.BVS',
    'easier68k.core.opcodes.Bcc.BPL',
    'easier68k.core.opcodes.Bcc.BMI',
    'easier68k.core.opcodes.Bcc.BGE',
    'easier68k.core.opcodes.Bcc.BLT',
    'easier68k.core.opcodes.Bcc.BGT',
    'easier68k.core.opcodes.Bcc.BLE'
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
