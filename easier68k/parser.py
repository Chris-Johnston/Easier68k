from lark import Lark
import os.path
from .assembly_transformer import AssemblyTransformer
from .assembly_transformer import Literal, Symbol
from .opcodes import get_opcode_parsed

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
    address = 1000
    list_file = {
    }
    symbols = {
    }
    equates = {
    }
    parsed_opcodes = []


    for label, op in result:
        op_name = op.name.lower()
        if label is not None and op_name != "equ":
            # equ is a special case
            symbols[label.name.lower()] = address
        if op.name.lower() == "org": # special case
            # use the value of the first imm as the starting address
            address = op.arg_list[0].value
            # todo, sanity check this to prevent it doesn't get out of bounds
            print(f"ORG -- {address}")
            if label is not None:
                symbols[label.name.lower()] = address

        elif op.name.lower() == "end":
            # end
            print("END")

        elif op.name.lower() == "equ":
            # just insert all of the immediate data as-is
            print("EQU")
            print(f"ASSIGN {label} to {op.arg_list[0].value}")
            equates[label.name.lower()] = op.arg_list[0].value
        elif op.name.lower() == "dc":
            print("DC")
            print(op.arg_list)
            for arg in op.arg_list:
                print(arg)
                print(arg.__dict__)

                if isinstance(arg.value, Symbol):
                    continue

                if isinstance(arg.value, str):
                    str_b = arg.value.encode('utf-8')
                    list_file[address]=str_b
                    address += len(str_b)
                    # for b in str_b:
                    #     address+=1
                    print("inserting the string", str_b)
                    continue
                
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
            print("op arg list", op.arg_list)

            # need to have the symbols know their own locations
            # this whole system is busted
            # also need to support adding labels before lines
            if op.arg_list is not None:
                for i in range(len(op.arg_list)):
                    x = op.arg_list[i]
                    if isinstance(x, Literal):
                        literal = x.value
                        if isinstance(literal, Symbol):
                            sym_name = literal.symbol_name.lower()
                            # insert a awa
                            v = symbols[sym_name]
                            op.arg_list[i] = Literal(v)

            from .assemblers import assemblers
            a = assemblers[op_name.lower()]

            assembler_immediates = [] # I don't have any way to do look-aheads for symbols
            # wonder if I'd have to do a lazy load type deal where I could
            # check against a global table

            # set the immediates which belong to the assembler
            if op.arg_list:
                for arg in op.arg_list:
                    if isinstance(arg, Literal):
                        literal = arg.value
                        if isinstance(literal, Symbol):
                            # need to handle symbols and equates
                            # symbols can be inserted, equates cannot
                            print("Skipping symbol", literal, "in arg list")

                            sym_name = literal.symbol_name

                            if sym_name in equates.keys():
                                print('name was in equates', sym_name)
                                v = equates[sym_name]
                                assembler_immediates = v
                            else:

                                # insert the symbol name, look it up later
                                assembler_immediates = sym_name.lower()
                        else:
                            assembler_immediates = arg.value

            # include the immediates in this as well
            opcode = get_opcode_parsed(op.name.lower(), op.size, op.arg_list)

            # this is where the opcodes are stuck into the list file, should instead
            # save all of these and do this at the end after the symbols are determined
            # there is a gap here

            # save the opcode assembler and the opcode itself, this is so that the
            # assembly for it can be generated later
            # because the assemblers are re-used, there should not be any state that
            # is tracked by the assembler objects themselves
            parsed_opcodes.append((a, opcode))
            # for word in a.assemble_immediate(opcode.to_asm_values()):
            #     list_file[address] = word
            #     address += 2
            
            # list_file[address] = a.assemble(opcode.to_asm_values())
            # address += 2 # this is not correct

            # TODO 1/3: this is outdated, will be extended to opcode_assembler so that data doesn't have to be inserted
            # manually

    # check that all referenced symbols have been defined
    for assembler, op in parsed_opcodes:
        for word in assembler.assemble_immediate(op.to_asm_values(), op.get_immediates()):
            list_file[address] = word
            address += 2

    from .new_list_file import ListFile
    lf = ListFile()
    lf.memory_map = list_file
    lf.symbols = symbols
    lf.equates = equates
    lf.starting_address = symbols['start']
    return lf