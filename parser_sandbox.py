from easier68k.parser import parse, assemble

hello_world = '''
; Constants
CR  EQU     $0D
LF  EQU     $0A
BB EQU %111
AA EQU +1
AB EQU -1
AC EQU 1234

; need to make this smart and do several passes
MSG     DC.B    'trust me this is coming from 68k assembly', CR, LF, 0
MSDFG     DC.B    #'A', #'B', CR, LF, 0

start   ORG    #4000
        ; Output the prompt message
        LEA     MSG, A1 
        MOVE.W  #14, D0  ; TODO alignment is weird
        TRAP    #15     

        ; halt
        MOVE.B  #9, D0
        TRAP    #15


        SIMHALT             ; halt simulator

        END start
'''

input = '''
*-----------------------------------------------------------
* Title      : looping
* Written by :
* Date       :
* Description: don't tell anyone but this is my hardware homework from 2 years ago
*-----------------------------------------------------------
    ORG $900
CRLF    DC.B $0D, $0A, 0 ; used for showing new lines

    ORG    $1000
    
START:                  ; first instruction of program

    ; set initial value of the value to be used for counting
    MOVE #1, D1 ; set D1 to 1
    MOVE #1024, D4 ; set max val to D4

LOOP:

    CMP D4, D1 ; compare the two
    
    BGT DONE ; if larger than the max then done
    
    ; display the value
    MOVE.B #3, D0 ; display signed number in D1 in decimal
    TRAP #15 ; display it
    
    ; show a new line
    LEA CRLF, A1 ; load CRLF str for \n
    MOVE.B #14, D0 ; set up for display
    TRAP #15 ; display it
    
    ; multiply D3 by 2
    ASL #1, D1 ; a logical shift left is the same thing as *2
    
    BRA LOOP ; loop again
    
DONE:
    

    SIMHALT             ; halt simulator

* Put variables and constants here

instOPList3 DC.W a,b,c,d      

    END    START        ; last line of source

*~Font name~Courier New~
*~Font size~10~
*~Tab type~1~
*~Tab size~4~
'''

just_add = '''

START:

  ADD #12, D1 ; simple stuff
  ADD D2, D1; set up d2 with a value first
  ; dont have imm values in memory working quite yet, need to set up parser to actually populate memory
  
  ;ADD D1, #1

  MOVE D2, D3 ; copy D2 into D3

  END START

'''

#input = just_add

input = hello_world
result = parse(input)
import pprint

print('----------------------')
pprint.pprint(result)

# start_address, list_file = assemble(result)
lf = assemble(result)
print("------------ LIST FILE --------")
pprint.pprint(lf.starting_address)
pprint.pprint(lf.memory_map)
pprint.pprint(lf.symbols)
pprint.pprint(lf.equates)

from easier68k.m68k import M68K
cpu = M68K()

# # load the list file
# for address in list_file.keys():
#     if isinstance(address, str): continue

#     from easier68k.op_size import OpSize
#     from easier68k.memory_value import MemoryValue
#     print("address", address, list_file[address])
#     cpu.memory.set(OpSize.WORD, address, MemoryValue(OpSize.WORD, unsigned_int=list_file[address]))
cpu.load_new_list_file(lf)
cpu.set_program_counter_value(lf.starting_address)

print("running ---")
cpu.run()