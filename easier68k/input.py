def get_input():
    """
    Wrap input in this method so that it can be wrapped with @patch in tests
    :return:
    """
    return input('')