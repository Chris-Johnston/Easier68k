from easier68k.parser import parse, assemble

hello_world = '''
; Constants
CR  EQU     $0D
LF  EQU     $0A
BB EQU %111
AA EQU +1
AB EQU -1
AC EQU 1234

start   ORG    $1000
        ; Output the prompt message
        LEA     MSG, A1 
        MOVE.B  #14, D0 
        TRAP    #15     

        ; halt
        MOVE.B  #9, D0
        TRAP    #15

MSG     DC.B    'This is some text', CR, LF, 0
MSDFG     DC.B    #'A', #'B', CR, LF, 0

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
CRLF
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

  ADD #1, D1 ; simple stuff

  END START

'''

input = just_add

result = parse(input)
import pprint

print('----------------------')
pprint.pprint(result)

assemble(result)