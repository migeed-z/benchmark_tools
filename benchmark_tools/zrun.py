import os,sys
from benchmark_tools.Reader import gen_all
from benchmark_tools.Runner import run_all
from argparse import ArgumentParser

def main():

    parser = ArgumentParser()
    parser.add_argument("rand")
    args = parser.parse_args(sys.argv[1:])

    rand = int(args.rand)

    if rand:
        while True:
            run_benchmark(True)
    else:
        run_benchmark(False)



def run_benchmark(rand):
    target = "./Benchmark"
    if os.path.exists('typed'):
        rand_and_ref = gen_all('typed', target, rand=rand)
        run_all(target,
                './Test',
                './output.txt', rand=rand_and_ref)
    else:
        print('No typed folder')

