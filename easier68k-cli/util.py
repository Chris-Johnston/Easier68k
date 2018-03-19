import glob


def split_args(args, required=0, optional=0):
    """
    splits the args string by comma and removes left and right whitespace.
    enforces that the amount of args is >= required and <= required+optional.
    if it is not then an error message is printed and None is returned
    """
    args = [x.strip() for x in args.split(',')]
    length = len(args)
    
    # one empty element does not count!
    if(length == 1 and not args[0]):
        length = 0
        args = []
    
    if(length < required):
        print('[ERROR] recieved ' + str(length) + ' arguments, but required ' + str(required) + ' arguments')
        return None
    elif(length > required+optional):
        print('[ERROR] recieved ' + str(length) + ' arguments, but accepts no more than ' + str(required+optional) + ' arguments')
        return None
    else:
        return args


def long_hex(number):
    """
    converts number to hex just like the inbuilt hex function but also
    pads zeroes such that there are always 8 hexidecimal digits
    """
    
    value_hex = hex(number)
    
    # pad with 0's. use 10 instead of 8 because of 0x prefix
    if(len(value_hex) < 10):
        value_hex = value_hex[0:2] + '0'*(10-len(value_hex)) + value_hex[2:]
    
    return value_hex

def autocomplete_getarg(line):
    """
    autocomplete passes in a line like: get_memory arg1, arg2
    the arg2 is what is being autocompleted on so return that
    """
    # find last argument or first one is seperated by a space from the command
    before_arg = line.rfind(',')
    if(before_arg == -1):
        before_arg = line.find(' ')
    
    assert before_arg >= 0
    
    # assign the arg. it skips the deliminator and any excess whitespace
    return line[before_arg+1:].lstrip()


def autocomplete_file(line):
    """
    helper that autocompletes files
    """
    arg = autocomplete_getarg(line)
    
    files = glob.glob(arg + "*")
    return files
    