from lark import Lark
import os.path
from .assembly_transformer import AssemblyTransformer
from .opcode_base import get_opcode_parsed

def parse(text: str):
    grammar_dir = os.path.dirname(__file__)
    grammar_file = os.path.join(grammar_dir, "68k_grammar.lark")

    with open(grammar_file) as grammar:
        l = Lark(grammar)
        tree = l.parse(text)
    result = AssemblyTransformer().transform(tree)
    return result

def assemble(result: list):
    address = 0
    for label, op in result:
        if op.name.lower() == "org": # special case
            # use the value of the first imm as the starting address
            address = op.arg_list[0].value
            # todo, sanity check this to prevent it doesn't get out of bounds
            print(f"ORG -- {address}")
        elif op.name.lower() == "end":
            # end
            print("END")

        elif op.name.lower() == "equ":
            # just insert all of the immediate data as-is
            print("EQU")

        else:
            print(f"op - {op.name.lower()}")
            op = get_opcode_parsed(op.name.lower(), op.size, op.arg_list)
        # any normal op
        # get the opcode for it
        # then have that opcode spit out the asm values for it
        # then send those into the assembler
        # then shove the assmebled op and the arg list (if immediate data)

    return None