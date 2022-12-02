import requests
from itertools import cycle

URL = "https://adventofcode.com/{year}/day/{day}/input"

def get_problem_input(year: int=2022, day: int=1):
    """TODO: figure out how to log in"""
    link = URL.format(year=year, day=day)
    f = requests.get(link)
    print(f.text)


def aoc_day2(fp, part2=False):
    """Rock paper scissors

    :param fp:
    :return:
    """
    def get_score(p1, p2):
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


    inp = open(fp).readlines()
    return sum(
        map(
            lambda x: get_score(*x.rstrip().split()), inp
        )
    )




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(aoc_day2('tests/2.txt'))
    print(aoc_day2('input/2.txt'))
    print(aoc_day2('tests/2.txt', True))
    print(aoc_day2('input/2.txt', True))