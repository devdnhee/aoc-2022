import math
import re

RE_COMMAND = re.compile(r"^([RLUD])\s(\d+)\s*$")


class Rope:
    DIRECTIONS = {
        "R": complex(1, 0),
        "L": complex(-1, 0),
        "U": complex(0, 1),
        "D": complex(0, -1),
    }

    def __init__(self, head, n_knots=2):
        self.rope = n_knots * [complex(*head)]
        self.state_history = [tuple(self.rope)]
        self.length = n_knots

    def is_adjacent(self, node1, node2):
        return abs(node1 - node2) <= math.sqrt(2)

    def check_diagonal(self, node1, node2):
        return node1.real != node2.real and node1.imag != node2.imag

    def check_gap(self, node1, node2):
        return abs(node1 - node2) == 2

    def diagonal_direction(self, delta):
        return complex(abs(delta.real) / delta.real, abs(delta.imag) / delta.imag)

    def make_move(self, direction):
        # make move on head
        self.rope[0] += Rope.DIRECTIONS[direction]

        for i in range(1, self.length):
            if self.is_adjacent(self.rope[i - 1], self.rope[i]):
                continue

            # move one step in direction to previous node if gap
            if self.check_gap(self.rope[i], self.rope[i - 1]):
                delta = self.rope[i - 1] - self.rope[i]
                self.rope[i] += delta / 2
                continue

            # diagonal movement
            delta = self.rope[i - 1] - self.rope[i]
            self.rope[i] += self.diagonal_direction(delta)

        self.state_history.append(tuple(self.rope))

    def run_command(self, command):
        direction, steps = RE_COMMAND.match(command).groups()
        steps = int(steps)
        for step in range(steps):
            self.make_move(direction)

    def nbr_different_tail_states(self):
        return len(set(map(lambda t: t[-1], self.state_history)))

    def __str__(self):
        min_x, max_x = min(int(min([r.real for r in self.rope])), 0), max(
            int(max([r.real for r in self.rope])), 0
        )
        min_y, max_y = min(int(min([r.imag for r in self.rope])), 0), max(
            int(max([r.imag for r in self.rope])), 0
        )
        grid = [(max_x - min_x + 1) * ["."] for i in range(max_y - min_y + 1)]
        grid[len(grid) + min_y - 1][-min_x] = "s"
        for idx, node in enumerate(self.rope):
            r = len(grid) - (int(node.imag) - min_y) - 1
            c = int(node.real) - min_x
            string = "H" if idx == 0 else idx
            grid[r][c] = f"{string}" if grid[r][c] == "." else f"{grid[r][c]}{string}"
        s = "\n".join(["\t".join(row) for row in grid])
        return s


def simulation(fp, rope_length=2):
    commands = open(fp).readlines()

    state_machine = Rope((0, 0), rope_length)

    for command in commands:
        state_machine.run_command(command)
        # print(f"\n\n{command}\n{state_machine}")

    n_tail_states = state_machine.nbr_different_tail_states()
    return n_tail_states


if __name__ == "__main__":
    # First star
    print(simulation("../tests/9.txt"))
    # print(simulation("../input/9.txt"))

    # Second star
    print(simulation("../tests/9.txt", rope_length=10))
    print(simulation("../tests/9b.txt", rope_length=10))
    # print(simulation("../input/9.txt", rope_length=10))
