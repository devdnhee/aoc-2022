import re
import numpy as np

AIR = 0
SAND = 1
ROCK = 2
ABYSS = 3
LEAK = -1

MAP = {AIR: ".", SAND: "o", ROCK: "#", LEAK: "+"}


class Cave:
    def __init__(self, environment=None, sand_leak=None):
        self.environment = environment
        self.environment[sand_leak] = LEAK
        self.sand_leak = sand_leak
        self.abyss_threshold = np.argwhere(self.environment == ROCK)[0, :].max()

    def find_next_destination(self, r, c):
        if r < 0:
            # abyss
            return r, c
        if self.environment[r + 1, c] <= 0:
            # move down
            check = np.argwhere(self.environment[r + 1 :, c] > AIR)
            if len(check) == 0:
                # we fall in the abyss
                return -1, c
            r_new = r + np.argwhere(self.environment[r + 1 :, c] > AIR).min()
            return r_new, c
        elif self.environment[r + 1, c - 1] <= 0:
            # move diagonally left
            return r + 1, c - 1
        elif self.environment[r + 1, c + 1] <= 0:
            # move diagonally right
            return r + 1, c + 1
        # cannot move further
        return r, c

    def has_sand_in_abyss(self):
        return self.environment[-1, :].sum() > 0

    def has_filled_leak(self):
        return self.environment[self.sand_leak] == SAND

    def drop_grain_of_sand(self):
        # start at the leak
        r, c = self.sand_leak
        while True:
            r_new, c_new = self.find_next_destination(r, c)
            if (r, c) == (r_new, c_new):
                # grain is blocked, final destination
                break
            r, c = r_new, c_new
        self.environment[r, c] = SAND
        return r, c

    def __str__(self):
        first_column_show = (
            np.argwhere(self.environment != 0)[:, 1].min() - 1
        )  # -1 to show a bit of left side
        last_column_show = (
            np.argwhere(self.environment != 0)[:, 1].max() + 1
        )  # +1 to show a bit of right side
        environment_show = self.environment[:, first_column_show : last_column_show + 1]
        vfunc = np.vectorize(lambda x: MAP.get(x, "?"))
        environment_array = vfunc(environment_show)
        drawing = "\n".join(["".join(row) for row in environment_array.tolist()])
        return drawing

    @classmethod
    def draw_line(cls, environment, from_coord, to_coord, value=ROCK):
        if from_coord[0] == to_coord[0]:
            # draw horizontal line
            r = from_coord[0]
            c_from, c_to = (
                (from_coord[1], to_coord[1])
                if from_coord[1] < to_coord[1]
                else (to_coord[1], from_coord[1])
            )
            environment[r, c_from : c_to + 1] = value
        elif from_coord[1] == to_coord[1]:
            # draw vertical line
            c = from_coord[1]
            r_from, r_to = (
                (from_coord[0], to_coord[0])
                if from_coord[0] < to_coord[0]
                else (to_coord[0], from_coord[0])
            )
            environment[r_from : r_to + 1, c] = value
        else:
            raise Exception(f"Unexpected input {from_coord, to_coord}")

    @classmethod
    def from_string(cls, string, sand_leak=(0, 500), max_dimension=1000, floor=False):
        rocks = [
            [
                tuple(map(int, reversed(match.split(","))))
                for match in re.findall("\d+,\d+", line)
            ]
            for line in string.split("\n")
        ]
        # min_row = min([c[0] for r in rocks for c in r])
        max_row = max([c[0] for r in rocks for c in r])
        # min_column = min([c[1] for r in rocks for c in r])
        max_column = max([c[1] for r in rocks for c in r])
        n_cols = max(max_column, max_dimension) + 1
        n_rows = (
            max_row + 3
        )  # +1 for 0, +1 for under the deepest rock and detect abyss, +1 for floor

        environment = np.zeros((n_rows, n_cols))

        for rock in rocks:
            for idx in range(len(rock) - 1):
                Cave.draw_line(environment, rock[idx], rock[idx + 1], ROCK)

        if floor:
            environment[-1, :] = ROCK

        return Cave(environment=environment, sand_leak=sand_leak)


def simulation(fp):
    raw_input = open(fp).read()
    cave = Cave.from_string(raw_input)
    it = 0
    while not cave.has_sand_in_abyss():
        it += 1
        r, c = cave.drop_grain_of_sand()

    print(f"\nAfter Iteration {it} -> {r, c}\n{cave}\n")
    return it - 1


def simulation_part2(fp):
    raw_input = open(fp).read()
    cave = Cave.from_string(raw_input, floor=True)
    it = 0
    while not cave.has_filled_leak():
        it += 1
        r, c = cave.drop_grain_of_sand()
    return it


if __name__ == "__main__":
    print(simulation("../tests/14.txt"))
    # print(simulation("../input/14.txt"))
    print(simulation_part2("../tests/14.txt"))
    # print(simulation_part2("../input/14.txt"))
