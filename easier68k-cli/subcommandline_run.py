import cmd
from easier68k.simulator import m68k
from easier68k.core.models.list_file import ListFile
from easier68k.core.enum.register import Register

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
    
    def do_registers(self, args):
        pass # print out all the register values or just the specified one or set one
    
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