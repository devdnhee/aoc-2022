def get_priority(line):
    r1, r2 = line[: len(line) // 2], line[len(line) // 2 :]
    item = list(set(r1) & set(r2))[0]
    if item.islower():
        prio = ord(item) - ord("a") + 1
    elif item.isupper():
        prio = ord(item) - ord("A") + 27
    else:
        raise Exception("Unexpected result")
    return prio


def get_total_priority(fp):
    inp = open(fp).readlines()
    return sum(map(lambda x: get_priority(x.rstrip()), inp))


def get_common_elf_priority(l1, l2, l3):
    item = list(set(l1) & set(l2) & set(l3))[0]
    if item.islower():
        prio = ord(item) - ord("a") + 1
    elif item.isupper():
        prio = ord(item) - ord("A") + 27
    else:
        raise Exception("Unexpected result")
    return prio


def get_total_elf_priority(fp):
    inp = open(fp).read().split("\n")
    inp_per_3 = [inp[i : i + 3] for i in range(0, len(inp), 3)]
    return sum(map(lambda x: get_common_elf_priority(*x), inp_per_3))


if __name__ == "__main__":
    # First star
    print(get_total_priority("../tests/3.txt"))
    # print(get_total_priority("../input/3.txt"))

    # Second star
    print(get_total_elf_priority("../tests/3.txt"))
    print(get_total_elf_priority("../input/3.txt"))
