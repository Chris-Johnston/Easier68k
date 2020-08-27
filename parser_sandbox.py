from lark import Lark

language = '''

ANY_TEXT: /.+/
OP_PARAM_TEXT: /[a-zA-Z]*[a-zA-Z0-9]+/
OPCODE_TEXT: /[a-zA-Z]+/
LABEL: OPCODE_TEXT // equivalent

LITERAL_HEX: /\\$[a-fA-F0-9]+/
LITERAL_BIN: /%[01]+/
LITERAL_DEC: /#?[0-9]+/

// LITERAL: /[#$%]?[a-fA-F0-9]+/
literal: LITERAL_BIN | LITERAL_HEX | LITERAL_DEC

literal_list: literal ("," literal_list)?

// hopefully shouldn't interfere with 's?
// update: it do
// needs to be updated to be more robust
_LITERAL_ESCAPED_STRING_INNER: /[a-zA-Z0-9!?\\., ]+/
literal_escaped_string: "'" _LITERAL_ESCAPED_STRING_INNER "'"

// MESSAGE DC.B 'Hello world', 0 ; c str
string_literal: literal_escaped_string
    | literal_escaped_string literal_list

start: line*

// line: [special_op | regular_op]? comment? NEWLINE
line: line_content NEWLINE
line_content: comment
    | special_op comment?
    | regular_op comment?
    | label comment?

special_opcode: opcode // START, MESSAGE
regular_op: special_opcode? opcode opcode_params?
opcode_sizes: "B" | "W" | "L"
opcode: OPCODE_TEXT
    | OPCODE_TEXT "." opcode_sizes

special_op: "START" "ORG" "$" INT

// ?start_opcode : "START" "ORG" string

comment_start : "*" | ";"
comment : comment_start ANY_TEXT?

label: LABEL ":"

opcode_param : [OP_PARAM_TEXT | literal | string_literal | literal_list ]
opcode_params : opcode_param "," opcode_param
    | opcode_param

%import common.WORD
%import common.WS
%import common.INT
%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING
%import common._STRING_ESC_INNER
%import common.NEWLINE
%ignore WS
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

    END    START        ; last line of source

*~Font name~Courier New~
*~Font size~10~
*~Tab type~1~
*~Tab size~4~
'''

l = Lark(language)
print(l.parse(input).pretty())