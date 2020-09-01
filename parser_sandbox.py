from lark import Lark, Transformer

language = '''

ANY_TEXT: /.+/
OP_PARAM_TEXT: /[a-zA-Z]*[a-zA-Z0-9]+/
OPCODE_TEXT: /[a-zA-Z]+/
LABEL: /[a-zA-Z_][a-zA-Z0-9\\_\\-]*/
literal_symbol: LABEL // equivalent
//    | "%" LABEL // not correct?
//    | "$" LABEL

literal_char: "'" LITERAL_ESCAPED_CHAR_INNER "'"


d_reg: ("d"|"D")("0".."7")
a_reg: ("a"|"A")("0".."6")

// todo add lowercase sp and pc
register: "SP" | d_reg | a_reg | "PC"

// LITERAL_HEX: /\\$[a-fA-F0-9]+/
// LITERAL_BIN: /%[01]+/
// LITERAL_DEC: /-?[0-9]+/

BINDIGIT: "0" | "1"
HEXNUM: HEXDIGIT+
BINNUM: BINDIGIT+
literal_hex: "$" HEXNUM
literal_bin: "%" BINNUM
literal_dec: SIGNED_INT


//literal_hex: "$" /\\$[a-fA-F0-9]+/
//literal_bin: /%[01]+/
//literal_dec: /-?[0-9]+/


// LITERAL: /[#$%]?[a-fA-F0-9]+/
literal: literal_bin
    | literal_hex
    | literal_dec
    | literal_symbol
    | literal_char
    | literal_str

immediate: "#" literal

//literal_list: literal
//   | literal "," literal_list

// hopefully shouldn't interfere with 's?
// update: it do
// needs to be updated to be more robust
LITERAL_ESCAPED_CHAR_INNER: /[a-zA-Z0-9\\/\\(\\):.," \\-+]/
// _LITERAL_ESCAPED_STRING_INNER: /[a-zA-Z0-9\\/\\(\\):.," \\-+]+/
STR_INNER: /[a-zA-Z0-9\\/\\(\\):.," \\-+]+/
literal_str: "'" STR_INNER "'"

// MESSAGE DC.B 'Hello world', 0 ; c str
// string_literal: LITERAL_ESCAPED_STRING

start: (line_content WS_INLINE* NEWLINE)*

// line: [special_op | regular_op]? comment? NEWLINE

line_content: label? regular_op? comment?
    // | literal_assignment comment?

// special_opcode: opcode // START, MESSAGE
regular_op: opcode opcode_params?
OPCODE_SIZES: "B" | "W" | "L"
opcode: OPCODE_TEXT
    | OPCODE_TEXT "." OPCODE_SIZES

// special_op: "START" "ORG" "$" INT

// ?start_opcode : "START" "ORG" string

comment_start : "*" | ";"
comment : comment_start ANY_TEXT?

label: LABEL ":"?
// literal_assignment: LABEL "EQU" literal

addressing_mode: "-(" register ")"
    | "(" register ")+"
    | "(" register ")"
    | register
// register_list: register ("/" register)+
//     | register "-" register

opcode_param : addressing_mode
//    | register_list
    | immediate
    | literal
    // | literal_list
//    | string_literal

//opcode_params: opcode_param 
//    | opcode_param "," opcode_params

opcode_params: opcode_param ( "," opcode_param )*

%import common.WORD
%import common.DIGIT
%import common.HEXDIGIT
%import common.WS
%import common.WS_INLINE
%import common.INT
%import common.SIGNED_NUMBER
%import common.SIGNED_INT
%import common.ESCAPED_STRING
%import common._STRING_ESC_INNER
%import common.NEWLINE
%ignore WS
'''

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

input = hello_world


l = Lark(language)

tree = l.parse(input)

print(tree.pretty())
# print(l.parse(input).pretty())
# print(l.parse(input))

from typing import Optional

class Register():
  def __init__(self, register_name: str):
    self.register_name = register_name

class Literal():
  def __init__(self, value:  int): # 
    self.value = value

  def __str__(self):
    return f"<Literal {self.value}>"

class LabelMap():
  def __init__(self):
    self.map = {}

  def add(self, name: str, value: Optional[Literal] = None):
    # adds a new item to the symbol map if not already defined.
    # if value is None, indicates that the symbol was referenced
    # but without a definition
    if name in self.map:
      match_value = self.map[name]

      # only update if not None
      if match_value is not None and value is None:
        self.map[name] = value
    else:
      self.map[name] = value
  
  def get_value(self, name: str) -> Optional[Literal]:
    # gets an literal value for a symbol if it has been assigned
    if name in self.map:
      return self.map[name]
    return None

class Symbol():
  # either as referenced by a definition
  # or when assigned
  def __init__(self, symbol_name: str):
    self.symbol_name = symbol_name

class ParamList():
  def __init__(self, values: list):
    self.values = values

class Opcode():
  def __init__(self, name, size: Optional[str] = None):
    self.name = name
    self.size = size
    self.arg_list = None # ParamList
  
  def __str__(self):
    return f"[Op {self.name}.{self.size or ''}]"

  def __repr__(self):
    return str(self)

class Label():
  def __init__(self, name):
    self.name = name
  
  def __str__(self):
    return f"[lable {self.name}]"

  def __repr__(self):
    return str(self)

# discard comments for now

class AssemblyTransformer(Transformer):
  
  def regular_op(self, items):
    if len(items) == 1:
      op, op_list = items[0], None
    else:
      op, op_list = items
    print("op", op, "list", op_list)
    op.arg_list = op_list
    # return (op, op_list)
    return op
  
  def start(self, items):
    content = []

    for x in items:
      print(f"{type(x)} - {x}")
      if isinstance(x, dict):
        label = x.get("label")
        opcode = x.get("opcode")

        content.append((label, opcode))
        # need to associate the next opcode
        # with this label
        # also need to make a special case for "EQU"
        # which really only makes sense when assembling
        # need to let the EQU opcode know about the parameter list
        # following it
        # but, all opcode will have to know that already
        # so, maybe this doesn't require a special case after all
    return content

  def label(self, items):
    label_text = items[0]
    # return "LBL-" + label_text
    return Label(label_text)

  def line_content(self, items):
    # pull out the label, opcode
    label = None
    opcode = None

    for x in items:
      print(f".{type(x)} - {x}")
      if isinstance(x, Label):
        label = x
      elif isinstance(x, Opcode):
        opcode = x

    if label is not None and opcode is not None:
      return { "label": label, "opcode": opcode }
    return None

  def opcode_params(self, items):
    # return list(items)
    return items

  # this feels wrong, having so many methods that do the same thing
  def opcode_param(self, item):
    return item[0]

  def literal(self, item):
    return Literal(item[0])
  
  def opcode(self, items):
    if len(items) == 1:
      return Opcode(items[0])
    opcode_text, opcode_size = items
    return Opcode(opcode_text, opcode_size)

  def literal_hex(self, items):
    return int(items[0], 16)

  def literal_bin(self, items):
    return int(items[0], 2)

  def literal_dec(self, items):
    return int(items[0])

  def literal_str(self, items):
    return items[0]
  
  def literal_char(self, items):
    return ord(items[0])

  def literal_symbol(self, item):
    # Labels are where they are defined, Symbols are where they are used
    return Symbol(item[0])

  def immediate(self, item):
    return item[0]

  def d_reg(self, items):
    # return "D reg " + items[0]
    return Register(f"D{items[0]}")

  def a_reg(self, items):
    # return "A reg " + items[0]
    return Register(f"A{items[0]}")

  def register(self, items):
    # this is where we would map to an enum
    return Register(items[0])

  def line_inner(self, items):
    # print("line inner", items)
    return items[0]

  def addressing_mode(self, items):
    # this needs to break out into different addressing modes
    return items[0]

  # should this be a rule and not a terminal?
  def OPCODE_TEXT(self, item):
    return item

  # does this work?
  LABEL = lambda self, x: str(x)
  STR_INNER = lambda self, x: str(x)
  # line_inner = lambda self, x: x[0]
  

result = AssemblyTransformer().transform(tree)
# print(type(result)) # , result.pretty())
import pprint
pprint.pprint(result)

# expected output for hello world
"""
start
  line
    line_content
      comment
        comment_start
         Constants
    

  line
    line_content
      label     CR
      line_inner
        regular_op
          opcode        EQU
          opcode_params
            opcode_param
              literal   $0D
    

  line
    line_content
      label     LF
      line_inner
        regular_op
          opcode        EQU
          opcode_params
            opcode_param
              literal   $0A
    


  line
    line_content
      label     start
      line_inner
        regular_op
          opcode        ORG
          opcode_params
            opcode_param
              literal   $1000
      comment
        comment_start
         Output the prompt message
    

  line
    line_content
      line_inner
        regular_op
          opcode        LEA
          opcode_params
            opcode_param        MSG
            opcode_param        A1
       
    

  line
    line_content
      line_inner
        regular_op
          opcode
            MOVE
            opcode_sizes
          opcode_params
            opcode_param
              immediate
                literal 14
            opcode_param        D0
       
    

  line
    line_content
      line_inner
        regular_op
          opcode        TRAP
          opcode_params
            opcode_param
              immediate
                literal 15
           
    


  line
    line_content
      comment
        comment_start
         halt
    

  line
    line_content
      line_inner
        regular_op
          opcode
            MOVE
            opcode_sizes
          opcode_params
            opcode_param
              immediate
                literal 9
            opcode_param        D0
    

  line
    line_content
      line_inner
        regular_op
          opcode        TRAP
          opcode_params
            opcode_param
              immediate
                literal 15
    


  line
    line_content
      label     MSG
      line_inner
        regular_op
          opcode
            DC
            opcode_sizes
          opcode_params
            opcode_param
              literal
                literal_escaped_string
            opcode_param        CR
            opcode_param        LF
            opcode_param        0
    


  line
    line_content
      label     SIMHALT
      comment
        comment_start
         halt simulator
    


  line
    line_content
      label     END
      line_inner
        regular_op
          opcode        start
    """