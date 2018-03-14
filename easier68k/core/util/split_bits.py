
def split_bits(word : int, amounts : list):
    """
    takes in a word and a list of bit amounts and returns
    the bits in the word split up. See the doctests for concrete examples
    
    >>> [bin(x) for x in split_bits(0b1001111010000001, [16])]
    ['0b1001111010000001']
    
    >>> [bin(x) for x in split_bits(0b1001111010000001, [8,8])]
    ['0b10011110', '0b10000001']
    
    not the whole 16 bits!
    >>> [bin(x) for x in split_bits(0b1001111010000001, [8])]
    Traceback (most recent call last):
    AssertionError: expected to split exactly one word
    
    This is a test splitting MOVE.B (A1),D4
    >>> [bin(x) for x in split_bits(0b0001001010000100, [2,2,3,3,3,3])]
    ['0b0', '0b1', '0b1', '0b10', '0b0', '0b100']
    
    """
    nums = []
    pos = 0
    for amount in amounts:
        # get a group of "amount" 1's 
        mask = 2**amount - 1
        
        # shift mask to the left so it aligns where the last
        # iteration ended off
        shift = 16 - amount - pos
        mask = mask << shift
        
        # update location in the word
        pos += amount
        
        # extract the relavent bits
        bits = word & mask
        
        # shift back and insert the list to be returned
        nums.append(bits >> shift)
    
    assert pos == 16, 'expected to split exactly one word'
    
    return nums