
def get_score(p1, p2, part2=False):
    # Rock = 0, Paper = 1, Scissors = 2
    p1_tf, p2_tf = ord(p1) - ord('A'), ord(p2) - ord('X')

    if not part2:
        shape_score = p2_tf + 1
        # result = 2 -> win, result = 1 -> draw, result = 0 -> loss
        result_score = 3 * ((p2_tf - p1_tf + 1) % 3)
    else:
        # X -> 0, Y -> 3, Z -> 6
        result_score = 3 * p2_tf
        # eg.
        shape_score = (p1_tf + (p2_tf - 1)) % 3 + 1
    return shape_score + result_score


def get_total_score(fp, **kwargs):
    inp = open(fp).readlines()
    return sum(
        map(
            lambda x: get_score(*x.rstrip().split(), **kwargs), inp
        )
    )

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(get_total_score('tests/2.txt'))
    print(get_total_score('input/2.txt'))
    print(get_total_score('tests/2.txt', part2=True))
    print(get_total_score('input/2.txt', part2=True))