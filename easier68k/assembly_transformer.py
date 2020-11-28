from lark import Transformer
from typing import Optional
from .op_size import OpSize
from .ea_mode import EAMode
from .register import Register

# class Register():
#   def __init__(self, register_name: str):
#     self.register_name = register_name

class Literal():
  def __init__(self, value: int): # 
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
    self.location = None

class ParamList():
  def __init__(self, values: list):
    self.values = values

class Opcode():
  def __init__(self, name, size: Optional[str] = None):
    self.name = name

    # convert to OpSize here
    if size is None:
        self.size = OpSize.WORD
        # is this the right default, or do we infer from params
        # please dont infer from params, _please_
    else:
        size = size.lower()
        if size == "b":
            self.size = OpSize.BYTE
        elif size == "w":
            self.size = OpSize.WORD
        elif size == "l":
            self.size = OpSize.LONG
    self.arg_list = None # ParamList
  
  def __str__(self):
    return f"[Op {self.name} {self.size}]"

  def __repr__(self):
    return str(self)

class Label():
  def __init__(self, name):
    self.name = name.strip(':')
  
  def __str__(self):
    return f"[label {self.name}]"

  def __repr__(self):
    return str(self)

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
    print(f"LBL {items}")
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

    if opcode is not None:
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
    s = Symbol(item[0])
    s.location = 1337 # TODO: look up symbol locations
    return s

  def immediate(self, item):
    return item[0]

  def d_reg(self, items):
    # return "D reg " + items[0]
    # return Register(f"D{items[0]}")
    # hack but I don't care
    from .register import Register
    reg_map = {
        0: Register.D0,
        1: Register.D1,
        2: Register.D2,
        3: Register.D3,
        4: Register.D4,
        5: Register.D5,
        6: Register.D6,
        7: Register.D7,
    }
    reg_num = int(items[0])
    return reg_map[reg_num]

  def a_reg(self, items):
    # hack but I don't care
    from .register import Register
    reg_map = {
        0: Register.A0,
        1: Register.A1,
        2: Register.A2,
        3: Register.A3,
        4: Register.A4,
        5: Register.A5,
        6: Register.A6,
        7: Register.D7,
    }
    reg_num = int(items[0])
    return reg_map[reg_num]

  def register(self, items):
    # this is where we would map to an enum
    # return Register(items[0])
    # from .register import Register
    # val = items[0]
    # if val.lower() == "PC":
    #     return Register.PC
    val = items[0]
    from .register import Register
    if isinstance(val, Register):
        return val
    print("TODO reg")
    return val

  def line_inner(self, items):
    # print("line inner", items)
    return items[0]

  def addressing_mode(self, items):
    # this needs to break out into different addressing modes
    if len(items) == 1:
      reg = items[0]
      if Register.D0 <= reg <= Register.D7:
        return reg, EAMode.DRD
      else:
        return reg, EAMode.ARD
    return items

  # should this be a rule and not a terminal?
  def OPCODE_TEXT(self, item):
    return item

  # def ard(self, item):
  #   return (item, EAMode.ARD)
  
  def ari(self, item):
    return (item, EAMode.ARI)

  def aripd(self, item):
    return (item, EAMode.ARIPD)
  
  def aripi(self, item):
    return (item, EAMode.ARIPI)

  # does this work?
  LABEL = lambda self, x: str(x)
  STR_INNER = lambda self, x: str(x)
  # line_inner = lambda self, x: x[0]