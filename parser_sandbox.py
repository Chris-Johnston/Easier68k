from lark import Lark

language = '''

ANY_TEXT: /.+/
OP_PARAM_TEXT: /[a-zA-Z]*[a-zA-Z0-9]+/
OPCODE_TEXT: /[a-zA-Z]+/
LABEL: /[a-zA-Z0-9\\_\\-]+/
LITERAL_SYMBOL: LABEL // equivalent
    | "%" LABEL
    | "$" LABEL

literal_char: "#" literal_escaped_string

D_REGISTER: /[dD][0-7]/
A_REGISTER: /[aA][0-6]/

// todo add lowercase sp and pc
REGISTER: "SP" | D_REGISTER | A_REGISTER | "PC"

LITERAL_HEX: /\\$[a-fA-F0-9]+/
LITERAL_BIN: /%[01]+/
LITERAL_DEC: /-?[0-9]+/

// LITERAL: /[#$%]?[a-fA-F0-9]+/
literal: LITERAL_BIN
    | LITERAL_HEX
    | LITERAL_DEC
    | LITERAL_SYMBOL
    | literal_char
    | literal_escaped_string

immediate: "#" literal

//literal_list: literal
//   | literal "," literal_list

// hopefully shouldn't interfere with 's?
// update: it do
// needs to be updated to be more robust
_LITERAL_ESCAPED_STRING_INNER: /[a-zA-Z0-9\\/#$!?\\\\\\(\\):.," \\-\\+]+/
literal_escaped_string: "'" _LITERAL_ESCAPED_STRING_INNER "'"

// MESSAGE DC.B 'Hello world', 0 ; c str
// string_literal: literal_escaped_string

start: line*

// line: [special_op | regular_op]? comment? NEWLINE
line: line_content NEWLINE

// i think equ might be a problem, treat it as an op?
line_inner : regular_op

line_content: label? line_inner? comment? WS_INLINE*
    // | literal_assignment comment?

// special_opcode: opcode // START, MESSAGE
regular_op: opcode opcode_params?
opcode_sizes: "B" | "W" | "L"
opcode: OPCODE_TEXT
    | OPCODE_TEXT "." opcode_sizes

// special_op: "START" "ORG" "$" INT

// ?start_opcode : "START" "ORG" string

comment_start : "*" | ";"
comment : comment_start ANY_TEXT?

label: LABEL ":"?
// literal_assignment: LABEL "EQU" literal

addressing_mode: "-(" REGISTER ")"
    | "(" REGISTER ")+"
    | "(" REGISTER ")"
register_list: REGISTER ("/" REGISTER)+
    | REGISTER "-" REGISTER

opcode_param : OP_PARAM_TEXT
    | immediate
    | literal
    // | literal_list
//    | string_literal
    | addressing_mode
    | register_list

//opcode_params: opcode_param 
//    | opcode_param "," opcode_params

opcode_params: opcode_param ( "," opcode_param )*

%import common.WORD
%import common.WS
%import common.WS_INLINE
%import common.INT
%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING
%import common._STRING_ESC_INNER
%import common.NEWLINE
%ignore WS
'''

hello_world = '''
; Constants
CR  EQU     $0D
LF  EQU     $0A

start   ORG    $1000
        ; Output the prompt message
        LEA     MSG, A1 
        MOVE.B  #14, D0 
        TRAP    #15     

        ; halt
        MOVE.B  #9, D0
        TRAP    #15

MSG     DC.B    'This is some text', CR, LF, 0

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

input = hello_world


l = Lark(language)
print(l.parse(input).pretty())
# print(l.parse(input))