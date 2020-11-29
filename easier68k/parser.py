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
                print('aaaaa')
                for i in range(len(op.arg_list)):
                    x = op.arg_list[i]
                    print('bbbbb')
                    if isinstance(x, Literal):
                        literal = x.value
                        if isinstance(literal, Symbol):
                            sym_name = literal.symbol_name.lower()
                            print("aaaa symbol", sym_name)

                            # insert a awa
                            v = symbols[sym_name]
                            op.arg_list[i] = Literal(v)

            opcode = get_opcode_parsed(op.name.lower(), op.size, op.arg_list)

            from .assemblers import assemblers
            a = assemblers[op_name.lower()]
            list_file[address] = a.assemble(opcode.to_asm_values())
            address += 2 # this is not correct

            # insert arg list
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
                                list_file[address] = v
                            # elif sym_name in symbols.keys():
                            #     print('name was in symbols', sym_name)
                            #     v = equates[sym_name]
                            #     list_file[address] = v
                            else:
                                print('missin', sym_name)
                                list_file[address] = sym_name.lower()
                        else:
                            list_file[address] = arg.value
                        address += 2 # this is not correct
                        # need to have a way to determine size of immediates

            # print(f"got op {type(opcode)} op.name {op.name}")
            # asm_values = opcode.to_asm_values()

            # if op.name.lower() == "add":
                
            #     assembler = assemblers["add"]

            #     values = opcode.to_asm_values()
            #     print(f"got values {values}")
            #     result = assembler.assemble(values)

            #     print(f"assembled into {result:b}")

            #     from .binary_prefix_tree import BinaryPrefixTree
            #     asm_tree = BinaryPrefixTree(assemblers)
            #     new_assembler = asm_tree.get_assembler(result)

            #     print(f"got matching assembler {type(new_assembler)}")

            #     dis_values = new_assembler.disassemble_values(result)
            #     print(f"got {dis_values} back out")

            #     from .op_add import OpCodeAdd

            #     new_op = OpCodeAdd()
            #     new_op.from_asm_values(dis_values)

            #     print(f"new op {new_op}")
            
            # # this will not actually work because the immediate value has to be in memory
            # print("EXECUTING --- ")
            # opcode.execute(cpu)
            # print(f"D1 = {cpu.get_register(Register.D1)}")
        # any normal op
        # get the opcode for it
        # then have that opcode spit out the asm values for it
        # then send those into the assembler
        # then shove the assmebled op and the arg list (if immediate data)

    # gone through a whole pass
    for k in list_file.keys():
        v = list_file[k]
        if isinstance(v, str):
            if v in symbols.keys():
                print("inserted key", k, "for symbol", v)
                list_file[k] = symbols[v]

    from .new_list_file import ListFile
    lf = ListFile()
    lf.memory_map = list_file
    lf.symbols = symbols
    lf.equates = equates
    lf.starting_address = symbols['start']
    return lf