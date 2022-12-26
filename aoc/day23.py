import numpy as np
from enum import IntEnum
from itertools import cycle
from tqdm import tqdm

class Tile(IntEnum):
    OPEN = 0
    ELF = 1
    
class Direction(IntEnum):
    N = 0
    S = 1
    W = 2
    E = 3


class Field:
    
    DRAW_MAP = {
        Tile.ELF: '#',
        Tile.OPEN: '.',
    }
    
    DRAW_REVERSE_MAP = {v:k for k, v in DRAW_MAP.items()}
    
    DIRECTIONS = [
        complex(0, 1), # N
        complex(0, -1), # S
        complex(-1, 0), # W
        complex(1, 0), # E
    ]
    
    def __init__(self, elves):
        self.elves = {i: loc for i, loc in enumerate(elves)}
        self.position_requests = {}
        self._round = cycle(Direction)
        self.round_number = 0
        
    
    @classmethod
    def get_close_orientations(cls, orient):
        if orient in (Direction.N, Direction.S):
            return [
                Field.DIRECTIONS[orient],
                Field.DIRECTIONS[orient] + Field.DIRECTIONS[Direction.W],
                Field.DIRECTIONS[orient] + Field.DIRECTIONS[Direction.E]
            ]
        else:
            return [
                Field.DIRECTIONS[orient],
                Field.DIRECTIONS[orient] + Field.DIRECTIONS[Direction.N],
                Field.DIRECTIONS[orient] + Field.DIRECTIONS[Direction.S]
            ]
            
    
    @classmethod 
    def get_all_orientations(cls):
        return Field.DIRECTIONS + [
            Field.DIRECTIONS[Direction.N] + Field.DIRECTIONS[Direction.W],
            Field.DIRECTIONS[Direction.N] + Field.DIRECTIONS[Direction.E],
            Field.DIRECTIONS[Direction.S] + Field.DIRECTIONS[Direction.W],
            Field.DIRECTIONS[Direction.S] + Field.DIRECTIONS[Direction.E]
        ]
            
        
    @property
    def matrix(self):
        min_x, max_x = int(min(elf.real for elf in self.elves.values())), int(max(elf.real for elf in self.elves.values()))
        min_y, max_y = int(min(elf.imag for elf in self.elves.values())), int(max(elf.imag for elf in self.elves.values()))
        
        n_rows = max_y - min_y + 1
        n_cols = max_x - min_x + 1
        
        elves_normalized = (elf - complex(min_x, min_y) for elf in self.elves.values())
        matrix = np.zeros((n_rows, n_cols))
        for elf in elves_normalized:
            matrix[-int(elf.imag)-1, int(elf.real)] = Tile.ELF
            
        return matrix
    
    
    def push_elf_propositions(self):
        r = next(self._round)
        for elf, loc in self.elves.items():
            check_all_pos = {loc + o for o in Field.get_all_orientations()}
            if all(map(lambda p: p not in self.elves.values(), check_all_pos)):
                continue
            for i in range(4):
                d = Direction((r + i) % 4)
                orients = Field.get_close_orientations(d)
                check_pos = {loc + o for o in orients}
                if all(map(lambda p: p not in self.elves.values(), check_pos)):
                    self.position_requests[elf] = loc + Field.DIRECTIONS[d]
                    break
                    
    
    def execute_elf_propositions(self):
        seen = set()
        dupes = []

        for loc in self.position_requests.values():
            if loc in seen:
                dupes.append(loc)
            else:
                seen.add(loc)
                
        updates = {elf: loc for elf, loc in self.position_requests.items() if loc not in dupes}
        if len(updates) == 0:
            print("No elf movement!")
            self.position_requests = {}
            return False
        else:
            for elf, loc in updates.items():
                self.elves[elf] = loc
            self.position_requests = {}
            return True
        
    
    def play_rounds(self, n=10):
        if n is None:
            continue_flag = True
            while continue_flag:
                self.round_number += 1
                self.push_elf_propositions()
                continue_flag = self.execute_elf_propositions()
            return self.round_number
        else:
            for _ in tqdm(range(n)):
                self.round_number += 1
                self.push_elf_propositions()
                self.execute_elf_propositions()
            
    
    def count_empty_ground(self):
        rectangle = self.matrix
        return np.sum(rectangle == Tile.OPEN)
    
    
    @classmethod
    def from_string(cls, string, **kwargs):
        lines = string.split('\n')
        elves = []
        for row, line in enumerate(reversed(lines)):
            new_elves = [complex(col, row) for col, el in enumerate(line) if el == '#']
            elves.extend(new_elves)
                
        return Field(elves)


    def __str__(self) -> str:
        matrix = self.matrix
        vfunc = np.vectorize(lambda x: Field.DRAW_MAP.get(x, "?"))
        environment_array = vfunc(matrix)
        drawing = "\n".join(["".join(row) for row in environment_array.tolist()])
        return drawing


def solve_part1(fp):
    raw = open(fp).read()
    
    f = Field.from_string(raw.strip())
    f.play_rounds()
    
    return f.count_empty_ground()


def solve_part2(fp):
    raw = open(fp).read()
    
    f = Field.from_string(raw.strip())
    f.play_rounds(n=None)
    
    return f.round_number


# def solve_part2(fp):
#     raw = open(fp).read()
#     board_string, instructions = raw.split('\n\n')
    
#     test_case = 'test' in fp
#     board = Board.from_string(board_string, cube=True, test=test_case)
#     board.follow_instructions(instructions)

#     open('path.txt', 'w').write(str(board))
    
#     return board.get_pwd()


if __name__ == "__main__":
    print(solve_part1('tests/23.txt'))
    print(solve_part1('input/23.txt'))
    print(solve_part2('tests/23.txt'))
    print(solve_part2('input/23.txt'))
