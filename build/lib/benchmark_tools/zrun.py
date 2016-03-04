import os
from benchmark_tools.Reader import gen_all
from benchmark_tools.Runner import run_all

def main():
    if os.path.exists('typed'):
        gen_all('typed')
        run_all('.',
                './Test',
                './output.py')
    else:
        print('No typed folder')
