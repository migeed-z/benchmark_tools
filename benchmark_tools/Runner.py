import os
import glob
import subprocess
from shutil import copyfile, copytree

import itertools
from multiprocessing import Process
from math import log2
from benchmark_tools.Reader import get_name

BOTH = "both"
jobs = 4

def product(xs):
  prod = 1
  for x in xs:
    prod = prod * x
  return prod

def run_all(benchmark, test_root, output):
    """
    :param benchmark: Full path
    :param test_root: Full path
    :param output: path
    :return: None
    """
    if not os.path.exists(test_root):
      os.mkdir(test_root)
    directories = glob.glob('%s/*' % benchmark)
    names = [get_name(d) for d in directories]

    all_files = [glob.glob('%s/*' % d) for d in directories]
    lengths = [len(files) for files in all_files]
    num_configs = product((len(f) for f in all_files))

    if 0 == jobs:
      raise RuntimeError("Need a non-zero number of jobs")
    chunk_size = None
    if jobs < num_configs:
      chunk_size = int(num_configs / jobs)
    else:
      chunk_size = 1

    procs = []
    outs = []
    for i in range(jobs):
      if i < num_configs:
        offset = i * chunk_size
        o = "%s.%s" % (output, i)
        lo = offset
        hi = 1+offset+chunk_size
        test = os.path.join(test_root, str(i))
        if not os.path.exists(BOTH):
          os.mkdir(BOTH)
        if not os.path.exists(test):
          copytree(BOTH, test)
        p = Process(target=run_chunk, args=(all_files, lo, hi, lengths, names, test, o))
        procs.append(p)
        outs.append(o)
    [p.start() for p in procs]
    # Need to wait for chunks to finish
    [p.join() for p in procs]
    with open(output, "w") as f_out:
      for o in outs:
        with open(o, "r") as f_in:
          for line in f_in:
            print(line, file=f_out)
        os.remove(o)
    return


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

def run_chunk(all_files, lo, hi, lengths, names, test, output):

    with open(output, 'w') as out:
        print("Running benchmarks [%s, %s)" % (lo, hi))
        for files in itertools.islice(itertools.product(*all_files), lo, hi):
            print("Running: %s" % list(files))
            for name, file in zip(names, files):
                copyfile(file, '%s/%s.py' % (test, name))
            t = run_1(test)
            nums = [get_name(f) for f in files]
            tag = '-'.join(nums)
            print('%s   %s   %s' % (tag, count_types(nums, lengths), t), file=out)

def run_1(test):
    os.system("rm -rf __pycache__")
    os.system("rm -rf %s/__pycache__" % test)
    run(test)
    vals = []
    for i in range(3):
      vals.append(run(test))
    return sum(vals) / len(vals)

def run(test):
    output = str(subprocess.check_output('retic %s/main.py' % test, shell=True), encoding="utf-8")
    run_time = output.split("\n")[-2]
    return float(run_time)
