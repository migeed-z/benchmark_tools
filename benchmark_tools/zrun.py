# import os
# from benchmark_tools.Reader import gen_all
# from benchmark_tools.Runner import run_all
#
# def main():
#     target = "./Benchmark"
#     if os.path.exists('typed'):
#         gen_all('typed', target)
#         run_all(target,
#                 './Test',
#                 './output.txt')
#     else:
#         print('No typed folder')


import os
from benchmark_tools.Reader import gen_all_random

def main():
    target = "./Benchmark"
    if os.path.exists('typed'):
        gen_all_random('typed', target)
        # run_all_random(target,
        #         './Test',
        #         './output.txt')
    else:
        print('No typed folder')
