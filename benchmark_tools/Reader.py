import os
import sys
from copy import deepcopy
from ast import FunctionDef, parse, ClassDef, Module, Assign
from astor import to_source
from os import listdir
from os.path import isfile, join
from benchmark_tools.constants import *
from random import getrandbits, choice
from benchmark_tools.constants import *


def data_path(filename):
    this_package_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(this_package_path, filename)


def parse_ast(file_name):
    with open(file_name, "r") as f:
        return parse(f.read(), filename='<unknown>', mode='exec')

def all_configurations(parsed, file_name, output_directory, rand_bits=None):

    name = get_name(file_name)
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    file_directory = os.path.join(output_directory, name)
    if not os.path.exists(file_directory):
        os.mkdir(file_directory)

    if rand_bits:
        new_config = deepcopy(parsed)
        all_configurations_ast_random(new_config, rand_bits)
        all_configs = [new_config]
    else:
        all_configs = all_configurations_ast(parsed)
    i = 0
    for ast in all_configs:
        with open("%s/%s.py" % (file_directory, i), "w") as out:
            print(to_source(ast), file=out)
        i += 1

def get_name(fname):
    return fname.rsplit("/", 1)[-1].rsplit(".", 1)[0]

def scan_ast(ast):
    """
    Scans the AST to find the sequence of bits needed for random sampling
    :param ast: AST
    :return: number of bits needed
    """
    body = ast.body
    res = 0
    for node in body:

        if isinstance(node, FunctionDef):
            res += len(node.args.args) + 1

        elif isinstance(node, ClassDef):
            res += 1
            for f in node.body:
                if isinstance(f, FunctionDef):
                    res += len(f.args.args) + 1
    return res

def all_configurations_args(typed_args):
    """
    Returns list of args
    :param list_of_typed: arg
    :return: args were args[i].annotation = None
    """
    res = []
    l = len(typed_args.args)
    for i in range(2**l):
        new_args = deepcopy(typed_args)
        b = bin(i)[2:]
        b = ("0" * (l - len(b))) + b
        for j in range(len(b)):
            if "1" == b[j]:
                new_args.args[j].annotation = None
        res.append(new_args)
    return res


def get_random_list_args(typed_args, rand_bits):
    """
    Returns one set of random arguments for one function.
    :param list_of_typed: arg
    :param sequence of random bits
    :return: set of arguments annonated randomly
    """
    new_args = []
    new_res = deepcopy(typed_args)
    for arg in typed_args.args:
        new_arg = deepcopy(arg)
        annotate = rand_bits.pop(0)
        if not annotate:
            new_arg.annotation = None
        new_args.append(new_arg)
    new_res.args = new_args
    return new_res


def all_configurations_def(d, all=None):
    """
    Creates list of all possible FunctionDefs
    :param d: FunctionDef
    :return [FunctionDef ...]
    """
    args = d.args
    res = []
    list_of_args = all_configurations_args(args)

    for arg in list_of_args:
        new_def = deepcopy(d)
        new_def.args = arg
        res.append(new_def)
        new_def2 = deepcopy(new_def)
        new_def2.returns = None
        res.append(new_def2)

    if all:
        return res

    else:
        return [res[0], res[-1]]


def all_configurations_def_random(d, random_bits, all=None):
    """
    Mutates args randomly by turning annotations on/off
    :param d: FunctionDef
    :return [FunctionDef]
    """

    d.decorator_list = [dec for dec in d.decorator_list if dec.id == counter_decorator]
    d.args = get_random_list_args(d.args, random_bits)

    ann_return = random_bits.pop(0)
    if not ann_return:
        d.returns = None

def all_configurations_ast(ast):
    """
    Remove all types from AST
    :param ast: AST
    :return: [AST ...]
    """
    ast_copy = deepcopy(ast)
    body = ast_copy.body
    ast_list = []
    body_list = []

    for node in body:
        if isinstance(node, FunctionDef):
            node.decorator_list = [d for d in node.decorator_list if d.id == counter_decorator]
            body_list = branch(body_list, all_configurations_def(node))

        elif isinstance(node, ClassDef):

            node_no_dec = deepcopy(node)
            node_no_dec.decorator_list = []

            body_list1 = branch(body_list, all_configurations_ast(node))
            body_list2 = branch(body_list, all_configurations_ast(node_no_dec))
            body_list = body_list1 + body_list2

        else:
            body_list = branch(body_list, [node])

    for body in body_list:
        new_ast = deepcopy(ast)
        new_ast.body = body
        ast_list.append(new_ast)

    return ast_list


def all_configurations_ast_random(ast, rand_bits):
    """
    Remove all types from AST
    :param ast: AST
    :param rand_bits: The sequence of random numbers
    :return: None
    """
    body = ast.body
    for node in body:

        if isinstance(node, FunctionDef):
            all_configurations_def_random(node, rand_bits)

        elif isinstance(node, ClassDef):
            dec = rand_bits.pop(0)
            if not dec:
                node.decorator_list = []

            for f in node.body:
                if isinstance(f, FunctionDef):
                    all_configurations_def_random(f, rand_bits)

def branch(prefixes, suffixes):
    """
    Adds each suffix to the end of each prefix
    :param prefixes: List
    :param suffixes: List
    """
    res = []
    if not prefixes:
        return [[s] for s in suffixes]

    for p in suffixes:
        for q in prefixes:
            res.append(q + [p])
    return res


def scan_all_program(parsed):
    """
    gets number of bits for all program
    :param dir_path:
    :param target:
    :return:
    """
    total_bits = 0
    for p in parsed:
        total_bits += scan_ast(p)
    return total_bits


def gen_all(dir_path, target, rand=None):
    """
    Generates permutation on all files in
    dir_path
    :param dir_path: String
    :return: None
    """
    parsed = []

    all_files = get_all_files(dir_path)
    for f in all_files:
        p = os.path.join(dir_path, f)
        parsed.append(parse_ast(p))

    if rand:
        n = scan_all_program(parsed)
        rand = [choice([0,1]) for i in range(n)]

    all_files = get_all_files(dir_path)
    print("Generating configurations for %s" % all_files)
    for i in range(len(parsed)):
        all_configurations(parsed[i], all_files[i], target, rand_bits=rand)


def get_all_files(dir_path):
     return [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

