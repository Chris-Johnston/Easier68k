import cmd
import glob
import json
import sys

# cmd uses readline. controlling this directly is necessary sometimes
import readline

from easier68k.assembler import assembler
from easier68k.simulator import m68k
from easier68k.core.models.list_file import ListFile
from easier68k.core.enum.register import Register


from .split_args import split_args





class CLI(cmd.Cmd):
    prompt = '(easier68k) '
    def do_exit(self, args):
        """Exits the easier68k cli"""
        return True
    
    
    def do_assemble(self, args):
        args = split_args(args)
        length = len(args)
        if(length == 0 or length > 2):
            print('Expected 1 or two args. aborting.')
            return False
            
        try:
            in_file = open(args[0])
            
            out_file = open(args[1], 'w') if length == 2 else sys.stdout
            assembled, issues = assembler.parse(in_file.read(-1))
            
            
            pretty_json = json.loads(assembled.to_json())
            out_file.write(json.dumps(pretty_json, indent=4, sort_keys=True))
            if not issues:
                return
                
            print('----- ISSUES -----')
            for issue in issues:
                print('{}: {}\n'.format(issue[1], issue[0]))
            
            in_file.close()
            
            if length == 2:
                out_file.close()
        except FileNotFoundError as not_found:
            print('[Error] file: ' + str(not_found) + ' does not exist')
    
    def help_assemble(self):
        print('syntax: assemble in_file[, out_file]')
        print('reads in and assembles the assembly from in_file and outputs the list file to out_file if specified or to stdout')
        print('')
        
        
    # will transfer this to a sub-command line with options like step instruction, run, print registers, etc... 
    def do_run(self, args):
        args = split_args(args)
        length = len(args)
        
        if(length != 1):
            print('Expected 1 arg. aborting.')
            return False
        
        in_file = open(args[0])
        
        list_file = ListFile()
        list_file.load_from_json(in_file.read(-1))
        
        in_file.close()
        
        simulator = m68k.M68K()
        simulator.load_list_file(list_file)
        print(simulator.get_register_value(Register.A0))
        simulator.step_instruction()
        simulator.step_instruction()
        print(simulator.get_register_value(Register.A0))
    
    
    # for now make everything autocomplete with files
    # does not handle spaces
    def completedefault(self, text, line, begidx, endidx):
        # find last argument or first one is seperated by a space from the command
        before_arg = line.rfind(',')
        if(before_arg == -1):
            before_arg = line.find(' ')
        
        assert before_arg >= 0
        
        
        # assign the arg. it skips the deliminator and any excess whitespace
        arg = line[before_arg+1:].lstrip()
        
        files = glob.glob(arg + "*")
        return files
    
    
if __name__ == '__main__':
    # originally alot of undesired characters were included such as hypthen and '/' 
    readline.set_completer_delims(' ,')
    cli = CLI()
    
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