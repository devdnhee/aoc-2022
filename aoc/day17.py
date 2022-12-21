from itertools import cycle, islice
import numpy as np
from tqdm import tqdm
import pandas as pd


class Chamber:

    UNDERSCORE = [complex(0, 0), complex(1, 0), complex(2, 0), complex(3, 0)]
    # (1, 1) is not needed but makes visualisations easier
    PLUS = [complex(0, 1), complex(1, 0), complex(1, 1), complex(1, 2), complex(2, 1)]
    JAY = [complex(0, 0), complex(1, 0), complex(2, 0), complex(2, 1), complex(2, 2)]
    LINE = [complex(0, 0), complex(0, 1), complex(0, 2), complex(0, 3)]
    SQUARE = [complex(0, 0), complex(0, 1), complex(1, 0), complex(1, 1)]

    DRAW_MAP = {
        0: ".",
        1: "#",
        2: "|",
        3: "-",
        -1: "@",
    }

    MOVES = {
        ">": complex(1, 0),
        "<": complex(-1, 0),
        "^": complex(0, 1),
        "v": complex(0, -1),
    }

    ORDER = [UNDERSCORE, PLUS, JAY, LINE, SQUARE]

    TAIL_CHECK = 400

    @classmethod
    def move_rock(cls, rock, offset):
        return [r + offset for r in rock]

    def __init__(self, width=7) -> None:
        self._width = width
        self._height = 0
        self.environment = [complex(i, 0) for i in range(width)]
        self._falling_rock = None
        self.history = []

    @property
    def height(self):
        return int(self._height)

    @height.setter
    def height(self, value):
        self._height = value
        return self._height

    @property
    def floor(self):
        return int(
            min(map(lambda pos: pos.imag, self.environment[-Chamber.TAIL_CHECK :]))
        )

    @property
    def width(self):
        return int(self._width)

    @property
    def falling_rock(self):
        return self._falling_rock

    @falling_rock.setter
    def falling_rock(self, value):
        self._falling_rock = value
        return self._falling_rock

    def generate_rocks(self):
        for rock in cycle(Chamber.ORDER):
            rock = Chamber.move_rock(rock, complex(2, self.height + 4))
            yield rock

    @property
    def matrix(self):
        normalised_position = [pos - self.floor for pos in self.environment]
        # + 7 to get extra space for falling rocks!
        extra_head_space = 7
        n_rows, n_cols = (
            int(self.height - self.floor + 1 + extra_head_space),
            self.width + 2,
        )
        matrix = np.zeros((n_rows, n_cols))

        # floor
        for pos in normalised_position:
            r, c = int(n_rows - pos.imag - 1), int(pos.real) + 1
            matrix[r, c] = 1
        matrix[-1, :] = 3

        # walls
        matrix[:, [0, -1]] = 2

        # falling rock
        if self.falling_rock is not None:
            normalised_rock = [pos - self.floor for pos in self.falling_rock]
            for pos in normalised_rock:
                r, c = int(n_rows - 1 - pos.imag), int(pos.real) + 1
                matrix[r, c] = -1

        return matrix

    @property
    def df_simulation(self):
        df = pd.DataFrame(
            self.history, columns=["number_moves", "n_rocks", "height"]
        ).assign(
            height_rock_ratio=lambda df: df.height / df.n_rocks,
            moves_for_rock=lambda df: df["number_moves"].diff(),
        )
        return df

    def rock_to_matrix(self, rock):
        rock_matrix = np.zeros_like(self.matrix)
        n_rows, _ = rock_matrix.shape
        normalised_rock = [pos - self.floor for pos in rock]
        for pos in normalised_rock:
            r, c = int(n_rows - pos.imag - 1), int(pos.real) + 1
            rock_matrix[r, c] = 1
        return rock_matrix

    def check_move(self, move):
        moved_rock = Chamber.move_rock(self.falling_rock, move)
        if moved_rock[-1].real >= self.width or moved_rock[0].real < 0:
            return False
        if any(
            map(lambda pos: pos in self.environment[-Chamber.TAIL_CHECK :], moved_rock)
        ):
            return False
        return True

    def check_at_rest(self):
        if self.falling_rock is None:
            return True

    def update_environment(self):
        self.environment.extend(self.falling_rock)
        self.falling_rock = None

    def find_pattern_period(self, pattern_length):
        df = self.df_simulation
        if len(df) < 2 * pattern_length:
            # Impossible to detect a pattern
            return None

        # try to backtrack the last pattern we've seen
        pattern = df["moves_for_rock"].tail(pattern_length).values

        # take equal segments
        sequence = df["moves_for_rock"].values[len(df) % pattern_length :]
        split_sequence = np.hsplit(sequence, len(sequence) / pattern_length)

        # check where the pattern reoccurred
        matches = np.atleast_1d(
            np.squeeze(
                np.argwhere(list(map(lambda a: np.all(pattern == a), split_sequence)))
            )
        )
        block_index = np.unique(np.diff(matches))
        if len(block_index) == 0:
            return None
        elif len(block_index) == 1:
            return block_index[0] * pattern_length
        else:
            # Multiple patterns discovered!
            raise Exception(f"Multiple patterns found for min_f={pattern_length}")

    def simulation(self, moves, N=2022, find_repeats=False, pattern_length=2000):
        rock_generator = islice(self.generate_rocks(), N)
        moves_generator = cycle(moves)
        pattern_divisor = len(moves) * 5
        pattern_modulo = N % pattern_divisor

        print(f"Start simulation: N={N}, M={len(moves)}, min_freq={pattern_length}")
        n_rocks = 0
        cycle_period = None
        for m_idx, move_enc in enumerate(moves_generator):
            move = Chamber.MOVES[move_enc]
            if self.falling_rock is None:
                self.history.append((m_idx, n_rocks, self.height))
                if (
                    find_repeats
                    and cycle_period is None
                    and n_rocks > 1
                    and n_rocks % pattern_divisor == pattern_modulo
                ):
                    print(
                        f"Checking for pattern after {n_rocks} rocks: pattern_length={pattern_length}"
                    )
                    cycle_period = self.find_pattern_period(pattern_length)
                    self.df_simulation.to_csv("df_simulation.csv")
                    if cycle_period is not None:
                        print(
                            f"Detected pattern after {n_rocks} rocks: cycle_period={cycle_period}"
                        )

                if cycle_period is not None and (
                    n_rocks % cycle_period == N % cycle_period
                ):
                    height_per_cycle = (
                        self.height - self.df_simulation.iloc[-cycle_period - 1].height
                    )
                    remaining_cycles = (N - n_rocks) / cycle_period
                    height = self.height + remaining_cycles * height_per_cycle
                    print(f"Calculating height after {n_rocks} rocks: height={height}")
                    return height

                try:
                    self.falling_rock = next(rock_generator)
                    n_rocks += 1
                except StopIteration:
                    return self.height

            if self.check_move(move):
                self.falling_rock = Chamber.move_rock(self.falling_rock, move)

            if self.check_move(Chamber.MOVES["v"]):
                self.falling_rock = Chamber.move_rock(
                    self.falling_rock, Chamber.MOVES["v"]
                )
            else:
                self.environment.extend(self.falling_rock)
                self.environment = self.environment[-2 * Chamber.TAIL_CHECK :]
                self.height = int(
                    max(
                        map(
                            lambda pos: pos.imag,
                            self.environment[-Chamber.TAIL_CHECK :],
                        )
                    )
                )
                self.falling_rock = None

    def __str__(self) -> str:
        vfunc = np.vectorize(lambda x: Chamber.DRAW_MAP.get(x, "?"))
        environment_array = vfunc(self.matrix)
        drawing = "\n".join(["".join(row) for row in environment_array.tolist()])
        return drawing


def simulation(fp, **kwargs):
    move_list = open(fp).read().rstrip()

    chamber = Chamber()
    return chamber.simulation(move_list, **kwargs)


if __name__ == "__main__":
    # print(simulation('tests/17.txt', N=2022))
    # print(simulation('input/17.txt', N=2022))
    print(simulation("tests/17.txt", N=5000, find_repeats=True))
    print(simulation("tests/17.txt", N=1000000000000, find_repeats=True))
    print(simulation("input/17.txt", N=1000000000000, find_repeats=True))
