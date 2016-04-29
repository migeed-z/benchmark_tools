import os
import glob
import subprocess
from shutil import copyfile

import itertools
from math import log2
from benchmark_tools.Reader import get_name


def run_all(benchmark, test, output):
    """
    :param benchmark: Full path
    :param test: Full path
    :param output: path
    :return: None
    """
    print("hello from 'run_all'")
    if not os.path.exists(test):
      os.mkdir(test)
    directories = glob.glob('%s/*' % benchmark)
    names = [get_name(d) for d in directories]

    all_files = [glob.glob('%s/*' % d) for d in directories]
    lengths = [len(files) for files in all_files]

    print("got names = %s, got lengths = %s" % (names, lengths))
    with open(output, 'w') as out:
        print("Running benchmarks")
        for files in itertools.product(*all_files):
            print("Running: %s" % list(files))
            for name, file in zip(names, files):
                copyfile(file, '%s/%s.py' % (test, name))
            t = run_1(test)
            nums = [get_name(f) for f in files]
            tag = '-'.join(nums)
            print('%s   %s   %s' % (tag, count_types(nums, lengths), t), file=out)


def count_types(nums, lengths):
    """
    Number of typed functions across all the files
    :param nums: List of string
    :param lengths: lengths[i] is upper bound for nums[i]
    :return: Int, representing number of annotated functions in the file
    """
    total = 0
    for num, length in zip(nums, lengths):
        b = bin(int(num))[2:]
        l = int(log2(length))
        c = ("0" * (l - len(b))) + b
        total += sum([1 for bit in c if bit == '0'])

    return total

def run_1(test):
    os.system("rm -rf __pycache__")
    os.system("rm -rf %s/__pycache__" % test)
    run(test)
    vals = []
    for i in range(3):
      vals.append(run(test))
    return sum(vals) / len(vals)

def run(test):
    output = str(subprocess.check_output('retic %s/main.py' % test, shell=True)).split("\\n")
    run_time = output[-2]
    return float(run_time)
