import os

def data_path(filename):
    this_package_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(this_package_path, filename)

