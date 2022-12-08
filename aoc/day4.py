import re

RE_SECTIONS = re.compile("^(\d+)-(\d+),(\d+)-(\d+)\s*$")


def is_overlap(line, full=True):
    s1_min, s1_max, s2_min, s2_max = [int(g) for g in RE_SECTIONS.match(line).groups()]
    if full:
        return (s1_min <= s2_min and s1_max >= s2_max) or (
            s2_min <= s1_min and s2_max >= s1_max
        )
    else:
        return not (s1_max < s2_min or s2_max < s1_min)


def get_total_number_of_overlaps(fp, full=True):
    inp = open(fp).readlines()
    return sum(map(lambda x: is_overlap(x, full), inp))


if __name__ == "__main__":
    # First star
    print(get_total_number_of_overlaps("../tests/4.txt"))
    # print(get_total_number_of_overlaps("../input/4.txt"))

    # Second star
    print(get_total_number_of_overlaps("../tests/4.txt", full=False))
    # print(get_total_number_of_overlaps("../input/4.txt", full=False))
