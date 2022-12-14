import ast
import numpy as np

def read_input(fp):
    raw_inputs = open(fp).read().split('\n\n')
    pairs_string = map(lambda x: x.split('\n'), raw_inputs)
    pairs = map(lambda t: (ast.literal_eval(t[0]), ast.literal_eval(t[1])), pairs_string)
    return pairs

def read_packages(fp):
    raw_inputs = open(fp).readlines()
    packages = [ast.literal_eval(l.rstrip('\n')) for l in raw_inputs if l != '\n']
    return packages


def compair(left, right):
    if type(left) != type(right):
        if type(left) == int:
            left = [left]
        elif type(right) == int:
            right = [right]

    if type(left) == type(right) == int:
        if left < right:
            return True
        elif left > right:
            return False
    else:
        decision = None
        if len(left) < len(right):
            decision =  True
        elif len(left) > len(right):
            decision = False
        for v1, v2 in zip(left, right):
            comparison = compair(v1,v2)
            if comparison is None:
                continue
            else:
                return comparison
        return decision


def merge(s1, s2):
    merged = []
    idx_s1 = 0
    idx_s2 = 0
    while idx_s1 < len(s1) and idx_s2 < len(s2):
        if compair(s1[idx_s1], s2[idx_s2]):
            merged.append(s1[idx_s1])
            idx_s1 += 1
        else:
            merged.append(s2[idx_s2])
            idx_s2 += 1

    if idx_s1 == len(s1):
        merged.extend(s2[idx_s2:])
    elif idx_s2 == len(s2):
        merged.extend(s1[idx_s1:])
    return merged


def merge_sort_packages(packages):
    N = len(packages)
    if N == 1:
        return packages
    if N == 2:
        if compair(packages[0], packages[1]):
            return [packages[0], packages[1]]
        else:
            return [packages[1], packages[0]]

    s1 = merge_sort_packages(packages[:N//2])
    s2 = merge_sort_packages(packages[N//2:])
    return merge(s1, s2)

def sum_index_sorted(fp):
    pairs = list(read_input(fp))
    results = [compair(l, r) for l, r in pairs]
    s1 = np.sum(np.argwhere(results) + 1)
    return s1

def sort_packages(fp):
    packages = read_packages(fp)
    sorted_packages = merge_sort_packages(packages)
    return sorted_packages

def get_decoder_key(fp, dividers=[[[2]], [[6]]]):
    packages = read_packages(fp) + dividers
    sorted_packages = merge_sort_packages(packages)
    d1 = sorted_packages.index(dividers[0]) + 1
    d2 = sorted_packages.index(dividers[1]) + 1
    return d1 * d2

if __name__ == "__main__":
    print(sum_index_sorted("../tests/13.txt"))
    # print(sum_index_sorted("../input/13.txt"))
    # print(get_decoder_key("../tests/13.txt"))
    print(get_decoder_key("../input/13.txt"))