from itertools import cycle, islice
import numpy as np
from tqdm import tqdm

class Chamber:
    
    UNDERSCORE = [complex(0, 0), complex(1, 0), complex(2, 0), complex(3, 0)]
    # (1, 1) is not needed but makes visualisations easier
    PLUS = [complex(0, 1), complex(1, 0), complex(1, 1), complex(1, 2), complex(2, 1)]
    JAY = [complex(0, 0), complex(1, 0), complex(2, 0), complex(2, 1), complex(2, 2)]
    LINE = [complex(0, 0), complex(0, 1), complex(0, 2), complex(0, 3)]
    SQUARE = [complex(0, 0), complex(0, 1), complex(1, 0), complex(1, 1)]
    
    DRAW_MAP = {
        0: '.',
        1: '#',
        2: '|',
        3: '-',
        -1: '@',
    }
    
    MOVES = {
        '>': complex(1, 0),
        '<': complex(-1, 0),
        '^': complex(0, 1),
        'v': complex(0, -1)
    }
    
    ORDER = [
        UNDERSCORE, PLUS, JAY, LINE, SQUARE
    ]
    
    @classmethod
    def move_rock(cls, rock, offset):
        return [r + offset for r in rock]
    
    def __init__(self, width=7) -> None: 
        self._width = width
        self.environment = [
            complex(i, 0) for i in range(width)
        ]
        self._falling_rock = None


    @property
    def height(self):
        return int(max(map(lambda pos: pos.imag, self.environment)))
    
    
    @property
    def floor(self):
        return int(min(map(lambda pos: pos.imag, self.environment)))
    
    
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
        n_rows, n_cols = int(self.height - self.floor + 1 + extra_head_space), self.width + 2
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
        # rock_matrix = self.rock_to_matrix(moved_rock)
        # return np.sum(np.logical_and(self.matrix > 0, rock_matrix > 0)) == 0
        if moved_rock[-1].real >= self.width or moved_rock[0].real < 0:
            return False
        if any(map(lambda pos: pos in self.environment, moved_rock)):
            return False
        return True
    
    
    def check_at_rest(self):
        if self.falling_rock is None:
            return True
        
    
    def update_environment(self):
        self.environment.extend(self.falling_rock)
        self.falling_rock = None
                
                
    def simulation(self, moves, N=2022):
        rock_generator = islice(self.generate_rocks(), N)
        moves_generator = cycle(moves)
        for move_enc in moves_generator:
            move = Chamber.MOVES[move_enc]
            if self.falling_rock is None:
                try:
                    self.falling_rock = next(rock_generator)
                except StopIteration:
                    return self.height

            if self.check_move(move):
                self.falling_rock = Chamber.move_rock(self.falling_rock, move)
            
            if self.check_move(Chamber.MOVES['v']):
                self.falling_rock = Chamber.move_rock(self.falling_rock, Chamber.MOVES['v'])
            else:
                self.environment.extend(self.falling_rock)
                self.falling_rock = None
                
        
    def __str__(self) -> str:
        vfunc = np.vectorize(lambda x: Chamber.DRAW_MAP.get(x, "?"))
        environment_array = vfunc(self.matrix)
        drawing = "\n".join(["".join(row) for row in environment_array.tolist()])
        return drawing


def simulation(fp, N):
    move_list = open(fp).read().rstrip()
    
    chamber = Chamber()
    chamber.simulation(move_list, N)
    
    return chamber.height


if __name__ == '__main__':
    print(simulation('tests/17.txt', N=2022))
    print(simulation('input/17.txt', N=2022))
