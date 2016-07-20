import os
import glob
import subprocess
from shutil import copyfile, copytree

import itertools
from multiprocessing import Process
from math import log2
from benchmark_tools.Reader import get_name

BOTH = "both"

def product(xs):
  prod = 1
  for x in xs:
    prod = prod * x
  return prod

def run_all(benchmark, test_root, output, rand=None):
    """
    :param benchmark: Full path
    :param test_root: Full path
    :param output: path
    :param rand: A tuple consisting of number of bits per file and random bits
    :type rand: ([int, ...], [0/1, ...])
    :return: None
    """
    jobs = 4 if not rand else 4
    if not os.path.exists(test_root):
      os.mkdir(test_root)
    directories = sorted(glob.glob('%s/*' % benchmark))
    names = [get_name(d) for d in directories]

    all_files = [glob.glob('%s/*' % d) for d in directories]
    lengths = [len(files) for files in all_files]
    num_configs = product((len(f) for f in all_files))

    if jobs == 0:
      raise RuntimeError("Need a non-zero number of jobs")
    if jobs < num_configs:
      chunk_size = int(num_configs / jobs)
    else:
      chunk_size = 1

    procs = []
    outs = []
    for i in range(jobs):
        run_job(num_configs, chunk_size, test_root, output, i, all_files, lengths,names,rand, procs,outs)
    [p.start() for p in procs]
    # Need to wait for chunks to finish
    [p.join() for p in procs]
    with open(output, "w") as f_out:
      print("File Name: %s " % output)
      for o in outs:
        with open(o, "r") as f_in:
          for line in f_in:
            print(line, file=f_out, end="")
        os.remove(o)
    return


def run_job(num_configs, chunk_size, test_root, output, i, all_files, lengths, names,rand, procs,outs):
    if i < num_configs:
        offset = i * chunk_size
        o = "%s.%s" % (output, i)
        lo = offset
        hi = offset+chunk_size
        test = os.path.join(test_root, str(i))
        if not os.path.exists(BOTH):
          os.mkdir(BOTH)
        if not os.path.exists(test):
          copytree(BOTH, test)
        p = Process(target=run_chunk, args=(all_files, lo, hi, lengths, names, test, o, rand))
        procs.append(p)
        outs.append(o)


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

def run_chunk(all_files, lo, hi, lengths, names, test, output, rand=None):

    with open(output, 'a') as out:
        print("Running benchmarks (%s, %s)" % (lo, hi))
        for files in itertools.islice(itertools.product(*all_files), lo, hi):
            print("Running: %s" % list(files))
            for name, file in zip(names, files):
                copyfile(file, '%s/%s.py' % (test, name))
            t = run_1(test)
            nums = [get_name(f) for f in files]
            tag = '-'.join(nums)
            if rand:
                print("%s   %s   %s" % (rand[0], count_types(nums, lengths), t), file=out)
            else:
                print('%s   %s   %s' % (tag, count_types(nums, lengths), t), file=out)




def run_1(test):
    os.system("rm -rf __pycache__")
    os.system("rm -rf %s/__pycache__" % test)
    run(test)
    vals = []
    for i in range(3):
      vals.append(run(test))
    return vals

def run(test):
    output = str(subprocess.check_output('retic %s/main.py' % test, shell=True), encoding="utf-8")
    run_time = output.split("\n")[-2]
    return float(run_time)
