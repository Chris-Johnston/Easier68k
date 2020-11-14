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
    # this is a hack
    from .m68k import M68K
    from .register import Register
    cpu = M68K()
    from .memory_value import MemoryValue
    from .op_size import OpSize
    cpu.set_register(Register.D2, MemoryValue(OpSize.WORD, unsigned_int=0xbeef))

    address = 1000
    list_file = {
    }
    for label, op in result:
        op_name = op.name.lower()
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
        elif op.name.lower() == "dc":
            print("DC")
            print(op.arg_list)
            for arg in op.arg_list:
                print(arg)
                print(arg.__dict__)
                
                # this will have an issue for how the values are inserted into the bytearray
                # also this does not handle other immediates that are not byte values
                # like strings
                list_file[address] = arg.value

                if op.size == OpSize.BYTE:
                    address += 1
                elif op.size == OpSize.WORD:
                    address += 2
                else:
                    address += 4
                
            # insert the rest as literal data
            print(op)
        elif op_name == "start":
            print("START")
        else:
            print(f"op - {op.name.lower()}")
            opcode = get_opcode_parsed(op.name.lower(), op.size, op.arg_list)
            # list_file[address] = opcode.

            from .assemblers import assemblers
            a = assemblers[op_name.lower()]
            list_file[address] = a.assemble(opcode.to_asm_values())
            address += 2 # this is not correct

            from .assembly_transformer import Literal

            # insert arg list
            for arg in op.arg_list:
                if isinstance(arg, Literal):
                    list_file[address] = arg.value
                    address += 2 # this is not correct

            print(f"got op {type(opcode)} op.name {op.name}")
            asm_values = opcode.to_asm_values()

            if op.name.lower() == "add":
                
                assembler = assemblers["add"]

                values = opcode.to_asm_values()
                print(f"got values {values}")
                result = assembler.assemble(values)

                print(f"assembled into {result:b}")

                from .binary_prefix_tree import BinaryPrefixTree
                asm_tree = BinaryPrefixTree(assemblers)
                new_assembler = asm_tree.get_assembler(result)

                print(f"got matching assembler {type(new_assembler)}")

                dis_values = new_assembler.disassemble_values(result)
                print(f"got {dis_values} back out")

                from .opcode_base import OpCodeAdd

                new_op = OpCodeAdd()
                new_op.from_asm_values(dis_values)

                print(f"new op {new_op}")
            
            # this will not actually work because the immediate value has to be in memory
            print("EXECUTING --- ")
            opcode.execute(cpu)
            print(f"D1 = {cpu.get_register(Register.D1)}")
        # any normal op
        # get the opcode for it
        # then have that opcode spit out the asm values for it
        # then send those into the assembler
        # then shove the assmebled op and the arg list (if immediate data)

    return address, list_file