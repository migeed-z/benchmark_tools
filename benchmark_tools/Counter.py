from benchmark_tools.ProcessText import get_function_names_for_file, get_file_names

"""A counter for the number of times a function was called"""


def counted(f):
    def wrapped(*args, **kwargs):
        wrapped.calls += 1
        return f(*args, **kwargs)
    wrapped.calls = 0
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
    for f in file_names:
        res.extend(get_function_names_for_file(f))
    return res

def get_num_calls(dir_path):
    """
    Returns a dictionary of function names and the number of times
    they were called, in this directory
    :param dir_path: file path
    :return: {Str:Int, ....}
    """
    res = {}
    names = get_function_names_for_file(dir_path)
    for n in names:
        res[n] = n.calls
    return res






