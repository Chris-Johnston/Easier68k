# This *is* actually a necessary import due to using "reflection" style code further down
# noinspection PyUnresolvedReferences
from ..opcodes import *
from types import ModuleType
import sys

valid_opcodes_module = [
    'easier68k.core.opcodes.move'
]

valid_opcodes = [
    x.split('.')[-1].upper() for x in valid_opcodes_module
]

def find_module(opcode: str) -> (ModuleType, type): # classes are of type "type" Really python?
    """
    Finds the proper module and module class based on the opcode
    :param opcode: The opcode to search for
    :return: The module and class found (or (None, None) if it doesn't find any)
    """
    op_module = None
    op_class = None

    for m in valid_opcodes_module:
        mod = sys.modules[m]
        if mod.command_matches(opcode):
            op_module = mod
            op_class = getattr(op_module, op_module.class_name)

    return op_module, op_class
