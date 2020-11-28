class ListFile():
    def __init__(self):
        self.memory_map = {}
        self.symbols = {}
        self.equates = {}
        self.starting_address = 0