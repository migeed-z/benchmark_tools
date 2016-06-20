from benchmark_tools.ProcessText import get_function_names_for_file, get_file_names

"""A counter for the number of times a function was called"""

calls = {}

def counted(f):
    me = "%s.%s" % (__file__, f)
    def wrapped(*args, **kwargs):
        calls[me] += 1
        return f(*args, **kwargs)
    calls[me] = 0
    return wrapped

def get_func_names(dir_path):
    """
    Gets the number of function calls for
    all functions in this directory
    :param dir_path: path to dir
    :return:
    """
    res = []
    file_names = get_file_names(dir_path)
    print(file_names)
    for f in file_names:
        res.extend(get_function_names_for_file(f))
    return res

def get_num_calls():
    """
    Returns a dictionary of function names and the number of times
    they were called, in this directory
    :param dir_path: file path
    :return: {Str:Int, ....}
    """
    return calls






