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
