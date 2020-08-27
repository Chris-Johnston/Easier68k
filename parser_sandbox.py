from lark import Lark

language = '''

ANY_TEXT: /.+/
OP_PARAM_TEXT: /[a-zA-Z]*[a-zA-Z0-9]+/
OPCODE_TEXT: /[a-zA-Z]+/

LITERAL_HEX: /\\$[a-fA-F0-9]+/
LITERAL_BIN: /%[01]+/
LITERAL_DEC: /#?[0-9]+/

// LITERAL: /[#$%]?[a-fA-F0-9]+/
literal: [ LITERAL_BIN | LITERAL_HEX | LITERAL_DEC ]

literal_list: literal
    | "," literal_list

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

special_opcode: opcode // START, MESSAGE
regular_op: special_opcode? opcode opcode_params?
opcode: OPCODE_TEXT
    | OPCODE_TEXT "." ["B" | "W" | "L"]

special_op: "START" "ORG" "$" INT

// ?start_opcode : "START" "ORG" string

comment_start : "*" | ";"
comment : comment_start ANY_TEXT?

opcode_param : [OP_PARAM_TEXT | literal | string_literal ]
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
*------
* test
*-----

START ORG $1000
    LEA MESSAGE, A1     ; Message
    MOVE.B #14, D0      ; load trap
    TRAP #15            ; trap

MESSAGE DC.B 'HELLO WORLD',0 ; c str
LF  EQU $0D

    END START
'''

l = Lark(language)
print(l.parse(input).pretty())