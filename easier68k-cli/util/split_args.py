# later: may include a required arguments and optional arguments so it can throw errors
def split_args(args):
    return [x.strip() for x in args.split(',')]
