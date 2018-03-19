import cmd
import binascii
from easier68k.simulator.m68k import M68K
from easier68k.simulator.memory import Memory
from easier68k.core.models.list_file import ListFile
from easier68k.core.enum.register import Register
from util import split_args, long_hex, autocomplete_file, autocomplete_getarg

class Run_CLI(cmd.Cmd):
    prompt = '(easier68k.simulate) '
    def __init__(self, sim):
        super().__init__()
        self.simulator = sim

    def do_exit(self, args):
        """Exits the easier68k run sub-cli"""
        return True
    
    def do_run(self, args):
        self.simulator.clock_auto_cycle = True
        self.simulator.run()
        
    def do_step(self, args):
        self.simulator.clock_auto_cycle = False
        self.simulator.run()
    
    
    def do_set_register(self, args):
        args = split_args(args, 2, 0)
        if(args == None):
            return False
            
        # get the one passed in
        try:
            reg = Register[args[0]]
            value = int(args[1], 0) #let python automatically determine base
            self.simulator.set_register_value(reg, value)
        except KeyError:
            print('[ERROR] unrecognized register ' + args[0])
            return False
        
        
    
    def help_set_register(self):
        print('syntax: registers_set register, value')
        print('sets the value in register to value (decimal unless prefixed with 0x for hexidecimal)')
        
    
    def complete_set_register(self, text, line, begidx, endidx):
        arg = autocomplete_getarg(line).upper()
        return [x.name for x in Register if x.name.find(arg) == 0]
        
        
    def do_get_registers(self, args):
        args = split_args(args, 0, 1)
        if(args == None):
            return False
        
        if(len(args) == 0):
            output = ''
            for i, reg in enumerate(Register):
                value_hex = long_hex(self.simulator.get_register_value(reg))
                
                output += '{:<16}'.format(reg.name + ': ' + value_hex)
                if(i % 4 == 3):
                    output += '\n'
                
            print(output)
        else:
            # get the one passed in
            try:
                reg = Register[args[0]]
                value_hex = long_hex(self.simulator.get_register_value(reg))
                
                print(value_hex)
            except KeyError:
                print('[ERROR] unrecognized register ' + args[0])
                return False
    
    def complete_get_registers(self, text, line, begidx, endidx):
        arg = autocomplete_getarg(line).upper()
        return [x.name for x in Register if x.name.find(arg) == 0]
        
        
    def help_get_registers(self):
        print('syntax: registers_get [register]')
        print('if no register is selected then all of them are printed')
        print('if a register is selected then just that register is printed')
    
    
    
    def do_dump_memory(self, args):
        args = split_args(args, 1, 0)
        if(args == None):
            return False
            
        out_file = open(args[0], 'wb')
        self.simulator.save_memory(out_file)
        out_file.close()
        
    
    def help_dump_memory(self, args):
        print('syntax: dump_memory out_file')
        print('dumps the memory to the out_file.')
    
    def complete_dump_memory(self, text, line, begidx, endidx):
        return autocomplete_file(line)
    
    def do_load_memory(self, args):
        args = split_args(args, 1, 0)
        if(args == None):
            return False
            
        try:
            in_file = open(args[0], 'rb')
            self.simulator.load_memory(in_file)
            
            in_file.close()
            
        except FileNotFoundError as not_found:
            print('[Error] file: ' + str(not_found) + ' does not exist')
    
    def help_load_memory(self, args):
        print('syntax: load_memory in_file')
        print('loads the memory from the in_file.')
    
    def complete_load_memory(self, text, line, begidx, endidx):
        return autocomplete_file(line)
        
    
    
    def do_get_memory(self, args):
        args = split_args(args, 2, 0)
        if(args == None):
            return False
            
        memory = self.simulator.memory
        
        start = int(args[0], 0)
        length = int(args[1], 0)
        
        # round down to nearest multiple of 8 to keep alignment
        start -= start % 8
        
        for i in range(length):
            loc = start + i
            
            if(loc % 8 == 0):
                print(long_hex(loc), end='    ')
            
            ending = ' '
            if(i % 4 == 3):
                ending = '    '
            if(i % 8 == 7):
                ending = '\n'
            
            value_str = bytes(memory.get(Memory.Byte, loc)).hex()
            print(value_str, end=ending)
        print('') # newline
        
    def help_get_memory(self):
        print('syntax: get_memory start_idx, length')
        print('retrievs the memory in the range [start_idx, start_idx+length)')
        print('accessing values outside of memory causes an error')
        print('start_idx is rounded down to the nearest multiple of 8 to keep formatting alignment')
    
    
    
    def do_set_memory(self, args):
        args = split_args(args, 3, 0)
        if(args == None):
            return False
            
        memory = self.simulator.memory
        
        start = int(args[0], 0)
        length = int(args[1], 0)
        value = args[2]
        
        
        # trim off optional prefix
        if(value[0:2] == '0x'):
            value = value[2:]
        
        # check lengths
        if(len(value) % 2 != 0 or len(value) // 2 != length):
            print('length of value and given length do not match')
            return False
            
        for i in range(length):
            loc = start + i
            memory.set(Memory.Byte, loc, bytearray.fromhex(value[i*2:i*2+2]))
        
    def help_set_memory(self, args):
        print('syntax: get_memory start_idx, length, value')
        print('sets the memory in the range [start_idx, start_idx+length) to the value(which must be expressed in hex)')
        print('accessing values outside of memory causes an error')
        print('assigning a value larger or smaller than the range can hold is an error')
    
    # break points when we add that too!
    

def subcommandline_run(file_name):
    simulator = M68K()
    if(file_name != None):
        in_file = open(file_name)
        
        list_file = ListFile()
        list_file.load_from_json(in_file.read(-1))
        
        in_file.close()
        simulator.load_list_file(list_file)
    
    cli = Run_CLI(simulator)
    
    # only loops if Ctrl-C was pressed
    while True:
        try:
            cli.cmdloop()
            break
        except KeyboardInterrupt:
            # allow Ctrl-C to stop long operations
            # does not garuntee leaving them in a valid state
            # (look into delaying Ctrl-C until an instruction finishes somehow?)
            print('Recieved Interrupt')
