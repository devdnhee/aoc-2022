def get_calories(elf):
    food = elf.split("\n")
    return sum(map(int, food))


def get_max_calories(fp):
    inp = open(fp).read().split("\n\n")
    return max(map(get_calories, inp))


def get_sum_top_3_calories(fp):
    inp = open(fp).read().split("\n\n")
    return sum(list(reversed(sorted(map(get_calories, inp))))[:3])


if __name__ == "__main__":
    # first star
    print(get_max_calories("../tests/1.txt"))
    # print(get_max_calories('../input/1.txt'))

    # second star
    print(get_sum_top_3_calories("../tests/1.txt"))
    # print(get_sum_top_3_calories('../input/1.txt'))
