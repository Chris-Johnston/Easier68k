"""
Contains a binary prefix tree implementation for assembling opcodes.
"""


class BinaryTreeNode():
    def __init__(self):
        self.left = None # 0
        self.right = None # 1
        self.value = None
        self.prefix = None
        self.length = None

class BinaryPrefixTree():
    def __init__(self, assemblers: list):
        # build the tree
        # add each assembler to the tree
        self.root_node = BinaryTreeNode()

        for a in assemblers.values():
            prefix, length = a.literal_prefix
            # print(f"op {a.get_opcode()} prefix: {prefix:b} len: {length}")
            root = self.root_node
            for bit_index in range(length, 0, -1):
                # mask the prefix for this bit
                prefix_bit_mask = (1 << (bit_index - 1))
                bit_value = (prefix & prefix_bit_mask) >> (bit_index - 1)
                if bit_value == 0:
                    if root.left is None:
                        root.left = BinaryTreeNode()
                    root = root.left
                else:
                    if root.right is None:
                        root.right = BinaryTreeNode()
                    root = root.right
            # out of bits, so assign the value of the root node
            root.value = a
            root.prefix = prefix
            root.length = length

        # build a tree / trie for all of the len = 2 prefixes
        # under that tree it will have a tree for the len = 4 prefixes

        # sort
    
    def get_assembler(self, word):
        root = self.root_node
        if root.left is None and root.right is None:
            return root.value

        # gets the longest prefix match
        for bit_index in range(16, 0, -1):
            
            # mask the prefix for this bit
            prefix_bit_mask = (1 << (bit_index - 1))
            bit_value = (word & prefix_bit_mask) >> (bit_index - 1)

            if bit_value == 0:
                if root.left is None:
                    # print('end left')
                    return root.value
                else:
                    root = root.left
            else:
                if root.right is None:
                    # print('end right')
                    return root.value
                else:
                    root = root.right
        return None
