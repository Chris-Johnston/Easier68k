class ListFile():
    def __init__(self):
        self.memory_map = {}
        self.symbols = {}
        self.equates = {}
        self.starting_address = 0
    
    def print(self):
        print("mem map", self.memory_map)
        print("sym", self.symbols)
        print("equ", self.equates)
        print("start", self.starting_address)