import os
import sys
from copy import deepcopy
from ast import FunctionDef, parse, ClassDef, Module, Assign
from astor import to_source
from os import listdir
from os.path import isfile, join
from benchmark_tools.constants import *
from random import choice

def data_path(filename):
    this_package_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(this_package_path, filename)


def all_configurations(file_name, output_directory):
    name = get_name(file_name)
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    file_directory = os.path.join(output_directory, name)
    if not os.path.exists(file_directory):
        os.mkdir(file_directory)
    with open(file_name, "r") as f:
        parsed = parse(f.read(), filename='<unknown>', mode='exec')
    all_configs = all_configurations_ast(parsed)
    i = 0
    for ast in all_configs:
        with open("%s/%s.py" % (file_directory, i), "w") as out:
            print(to_source(ast), file=out)
        i += 1

def all_configurations_random(file_name, output_directory):
    """
    Generates all configurations and outputs them in the output directory
    :param file_name:
    :param output_directory:
    :return:
    """
    name = get_name(file_name)
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    file_directory = os.path.join(output_directory, name)
    if not os.path.exists(file_directory):
        os.mkdir(file_directory)
    with open(file_name, "r") as f:
        parsed = parse(f.read(), filename='<unknown>', mode='exec')
    #this passes in a copy of the AST now
    new_config = deepcopy(parsed)
    all_configurations_ast_random(new_config)
    i = 0
    with open("%s/%s.py" % (file_directory, i), "w") as out:
        print(to_source(new_config), file=out)
    i += 1


def get_name(fname):
    return fname.rsplit("/", 1)[-1].rsplit(".", 1)[0]


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


def get_random_list_args(typed_args):
    """
    Returns one set of random arguments for one function.
    :param list_of_typed: arg
    :return: set of arguments annonated randomly
    """
    new_args = []
    new_res = deepcopy(typed_args)
    for arg in typed_args.args:
        new_arg = deepcopy(arg)
        annotate = choice([0, 1])
        if not annotate:
            # print("arg off %s" % new_arg)
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


def all_configurations_def_random(d, all=None):
    """
    Mutates args randomly by turning annotations on/off
    :param d: FunctionDef
    :return [FunctionDef]
    """
    d.args = get_random_list_args(d.args)
    annotate = choice([0, 1])
    if not annotate:
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



def all_configurations_ast_random(ast):
    """
    Remove all types from AST
    :param ast: AST
    :return: None
    """

    body = ast.body

    for node in body:

        if isinstance(node, FunctionDef):
            node.decorator_list = [d for d in node.decorator_list if d.id == counter_decorator]
            all_configurations_def_random(node)

        elif isinstance(node, ClassDef):
            dec = choice([0, 1])
            if not dec:
                node.decorator_list = []

            for f in node.body:
                if not isinstance(f, Assign):
                    print("before: %s" % f)
                    all_configurations_ast_random(f)




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


def gen_all(dir_path, target):
    """
    Generates permutation on all files in
    dir_path
    :param dir_path: String
    :return: None
    """
    all_files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    print("Generating configurations for %s" % all_files)
    for f in all_files:
        p = os.path.join(dir_path, f)
        all_configurations(p, target)


#TODO: abstract this
def gen_all_random(dir_path, target):
    """

    :param dir_path:
    :param target:
    :return:
    """
    all_files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    print("Generating configurations for %s" % all_files)
    for f in all_files:
        p = os.path.join(dir_path, f)
        all_configurations_random(p, target)