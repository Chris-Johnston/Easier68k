import cmd
import binascii
from easier68k.simulator import m68k
from easier68k.core.models.list_file import ListFile
from easier68k.core.enum.register import Register
from util.split_args import split_args

class Run_CLI(cmd.Cmd):
    prompt = '(easier68k.run) '
    def __init__(self, sim):
        super().__init__()
        self.simulator = sim

    def do_exit(self, args):
        """Exits the easier68k run sub-cli"""
        return True
    
    def do_run(self, args):
        pass # run the simulator
        
    def do_step(self, args):
        pass # run the simulator one instruction
    
    
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
        
        
        
    def do_get_registers(self, args):
        args = split_args(args, 0, 1)
        if(args == None):
            return False
        
        if(len(args) == 0):
            output = ''
            for i, reg in enumerate(Register):
                value_hex = hex(self.simulator.get_register_value(reg))
                
                # pad with 0's. use 10 instead of 8 because of 0x prefix
                if(len(value_hex) < 10):
                    value_hex = value_hex[0:2] + '0'*(10-len(value_hex)) + value_hex[2:]
                
                output += '{:<16}'.format(reg.name + ': ' + value_hex)
                if(i % 4 == 3):
                    output += '\n'
                
            print(output)
        else:
            # get the one passed in
            try:
                reg = Register[args[0]]
                value_hex = hex(self.simulator.get_register_value(reg))
                
                # pad with 0's. use 10 instead of 8 because of 0x prefix
                if(len(value_hex) < 10):
                    value_hex = value_hex[0:3] + '0'*(10-len(value_hex)) + value_hex[3:]
                
                print(value_hex)
            except KeyError:
                print('[ERROR] unrecognized register ' + args[0])
                return False
            
        
        
    def help_get_registers(self):
        print('syntax: registers_get [register]')
        print('if no register is selected then all of them are printed')
        print('if a register is selected then just that register is printed')
    
    def do_memory(self, args):
        pass # get a whole memory dump or just a region or set a region
    
    # break points when we add that too!
    

def subcommandline_run(file_name):
    in_file = open(file_name)
    
    list_file = ListFile()
    list_file.load_from_json(in_file.read(-1))
    
    in_file.close()
    
    simulator = m68k.M68K()
    simulator.load_list_file(list_file)
    
    #print(simulator.get_register_value(Register.A0))
    #simulator.step_instruction()
    #simulator.step_instruction()
    #print(simulator.get_register_value(Register.A0))
    
    
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