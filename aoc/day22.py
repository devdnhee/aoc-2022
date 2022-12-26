import numpy as np
import re
from enum import IntEnum
from tqdm import tqdm

RE_BOARD_ROW = re.compile(r'[\.#]+')
RE_INSTRUCTION = re.compile(r'\d+|[LR]')

class Tile(IntEnum):
    OPEN = 0
    WALL = 1
    # OOM = out of map
    OOM = -1
    # location
    LOC = 2
    PORTAL = 3
    RIGHT = 4
    DOWN = 5
    LEFT = 6
    UP = 7
    
class Direction(IntEnum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


class Board:
    
    DRAW_MAP = {
        Tile.OPEN: '.',
        Tile.WALL: '#',
        Tile.OOM: ' ',
        Tile.LOC: 'X',
        Tile.PORTAL: '~',
        Tile.RIGHT: '>',
        Tile.DOWN: 'v',
        Tile.LEFT: '<',
        Tile.UP: '^'
    }
    
    DRAW_REVERSE_MAP = {v:k for k, v in DRAW_MAP.items()}
    
    DIRECTIONS = [
        np.array([0, 1]), # RIGHT
        np.array([1, 0]), # DOWN
        np.array([0, -1]), # LEFT
        np.array([-1, 0]), # UP
    ]
    
    def __init__(self, board, cube=False, test=True):
        self.board = board
        self.initialise_board_metadata()
        self._position = np.argwhere(board >= Tile.OPEN)[0]
        self._direction = Direction.RIGHT
        self._walls = np.argwhere(self.board == Tile.WALL)
        self.cube = cube
        self.side = int(np.sqrt((self.board >= 0).sum() / 6))
        self.path = []
        if test:
            self.initialise_cube_portals_test()
        else:
            self.initialise_cube_portals_input()
        return
    
    
    def initialise_board_metadata(self):
        valid = np.argwhere(self.board >= Tile.OPEN)
        n_rows, n_cols = self.board.shape
        self.metadata = dict(rows=dict(), cols=dict())
        for r in range(n_rows):
            cols = valid[valid[:, 0] == r][:, 1]
            self.metadata['rows'][r] = dict(min=cols.min(), max=cols.max(), mod=cols.shape[0])
        for c in range(n_cols):
            rows = valid[valid[:, 1] == c][:, 0]
            self.metadata['cols'][c] = dict(min=rows.min(), max=rows.max(), mod=rows.shape[0])
    
    
    def initialise_cube_portals_test(self):
        """ Example config for side = 4
                1111
                1111
                1111
                1111
        222233334444
        222233334444
        222233334444
        222233334444
                55556666
                55556666
                55556666
                55556666
        """
        self.metadata['portals'] = dict()
        for i in range(self.side):
            # Between areas 1 and 3
            self.metadata['portals'][(self.side, self.side + i)] = np.array((i, 2 * self.side)), Direction.DOWN
            self.metadata['portals'][(i, 2 * self.side)] = np.array((self.side, self.side + i)), Direction.RIGHT
            
            # Between areas 1 and 2
            self.metadata['portals'][(0, 2 * self.side + i)] = np.array((self.side, self.side - 1 - i)), Direction.DOWN
            self.metadata['portals'][(self.side, self.side - 1 - i)] = np.array((0, 2 * self.side + i)), Direction.DOWN
            
            # Between areas 1 and 6
            self.metadata['portals'][(i, 3 * self.side - 1)] = np.array((3 * self.side - 1 - i, 4 * self.side - 1)), Direction.LEFT
            self.metadata['portals'][(3 * self.side - 1 - i, 4 * self.side - 1)] = np.array((i, 3 * self.side - 1)), Direction.LEFT

            # Between areas 2 and 5
            self.metadata['portals'][(2 * self.side - 1, self.side - 1 - i)] = np.array((3 * self.side - 1, 2 * self.side + i)), Direction.UP
            self.metadata['portals'][(3 * self.side - 1, 2 * self.side + i)] = np.array((2 * self.side - 1, self.side - 1 - i)), Direction.UP
                
            # Between areas 2 and 6
            self.metadata['portals'][(0, self.side + 1)] = np.array((3 * self.side - 1, 4 * self.side - i)), Direction.UP 
            self.metadata['portals'][(3 * self.side - 1, 4 * self.side - i) ] = np.array((0, self.side + 1)), Direction.RIGHT 
                
            # Between areas 3 and 5
            self.metadata['portals'][(2 * self.side - 1, self.side + i)] = np.array((3 * self.side - 1 - i, 2 * self.side)), Direction.RIGHT
            self.metadata['portals'][(3 * self.side - 1 - i, 2 * self.side)] = np.array((2 * self.side - 1, self.side + i)), Direction.UP
            
            # Between areas 4 and 6
            self.metadata['portals'][(self.side + i, 3 * self.side - 1)] = np.array((2 * self.side, 4 * self.side - 1 - i)), Direction.DOWN
            self.metadata['portals'][(2 * self.side, 4 * self.side - 1 - i)] = np.array((self.side + i, 3 * self.side - 1)), Direction.LEFT


    def initialise_cube_portals_input(self):
        """ my input config:
            1   2
            3    
        4   5
        6
        """
        self.metadata['portals'] = dict()
        for i in range(self.side):
            # Between areas 1 and 4
            self.metadata['portals'][(i, self.side)] = np.array((3 * self.side - 1 -i, 0)), Direction.RIGHT
            self.metadata['portals'][(3 * self.side - 1 -i, 0)] = np.array((i, self.side)), Direction.RIGHT
            
            # Between areas 1 and 6
            self.metadata['portals'][(0, self.side + i)] = np.array((3 * self.side + i, 0)), Direction.RIGHT
            self.metadata['portals'][(3 * self.side + i, 0)] = np.array((0, self.side + i)), Direction.DOWN
            
            # Between areas 2 and 3
            self.metadata['portals'][(self.side - 1, 2 * self.side + i)] = np.array((self.side + i, 2 * self.side - 1)), Direction.LEFT
            self.metadata['portals'][(self.side + i, 2 * self.side - 1)] = np.array((self.side - 1, 2 * self.side + i)), Direction.UP

            # Between areas 2 and 5
            self.metadata['portals'][(i, 3 * self.side - 1)] = np.array((3 * self.side - 1 - i, 2 * self.side - 1)), Direction.LEFT
            self.metadata['portals'][(3 * self.side - 1 - i, 2 * self.side - 1)] = np.array((i, 3 * self.side - 1)), Direction.LEFT
                
            # Between areas 2 and 6
            self.metadata['portals'][(0, 2 * self.side + i)] = np.array((4 * self.side - 1, i)), Direction.UP 
            self.metadata['portals'][(4 * self.side - 1, i)] = np.array((0, 2 * self.side + i)), Direction.DOWN 
                
            # Between areas 3 and 4
            self.metadata['portals'][(self.side + i, self.side)] = np.array((2 * self.side, i)), Direction.DOWN
            self.metadata['portals'][(2 * self.side, i)] = np.array((self.side + i, self.side)), Direction.RIGHT
            
            # Between areas 5 and 6
            self.metadata['portals'][(3 * self.side - 1, self.side + i)] = np.array((3 * self.side + i, self.side - 1)), Direction.LEFT
            self.metadata['portals'][(3 * self.side + i, self.side - 1)] = np.array((3 * self.side - 1, self.side + i)), Direction.UP
    
    
    def get_opposing_walls(self):
        if self._direction % 2 == 0:
            wall_pos = self._walls[self._walls[:, 0] == self.position[0]]
        else:
            wall_pos = self._walls[self._walls[:, 1] == self.position[1]]
        return wall_pos
    
    
    def get_distance_to_wall(self):
        wall_pos = self.get_opposing_walls()
        if self._direction % 2 == 0:
            modulo = self.metadata['rows'][self.position[0]]['mod']
            distance = (Board.DIRECTIONS[self._direction][1]*(wall_pos[:, 1] - self.position[1])) % modulo
        else:
            modulo = self.metadata['cols'][self.position[1]]['mod']
            distance = (Board.DIRECTIONS[self._direction][0]*(wall_pos[:, 0] - self.position[0])) % modulo
        return distance.min()
    
    
    @property
    def position(self):
        return self._position
    
    
    def check_oom(self, position):
        n_rows, n_cols = self.board.shape
        if position[0] >= n_rows or position[0] < 0 or position[1] >= n_cols or position[1] < 0:
            return True
        if self.board[tuple(position)] == Tile.OOM:
            return True
        return False  
    
    
    @position.setter
    def position(self, value):
        """Value is amount of steps to take in the current direction"""
        if not self.cube:
            distance_to_wall = self.get_distance_to_wall()
            value = min(value, distance_to_wall - 1)
            pos_oom = self.position + value * Board.DIRECTIONS[self._direction]
            if self._direction % 2 == 0:
                delta = self.metadata['rows'][pos_oom[0]]['min']
                modulo = self.metadata['rows'][pos_oom[0]]['mod']
                self._position[1] = delta + pos_oom[1] % modulo
            else: 
                # self._direction % 2 == 1
                delta = self.metadata['cols'][pos_oom[1]]['min']
                modulo = self.metadata['cols'][pos_oom[1]]['mod']
                self._position[0] = delta + pos_oom[0] % modulo
                
        else:
            # do 1 by one
            steps_to_take = value
            against_wall = False
            current_pos = self.position
            current_dir = self.direction
            while not against_wall and steps_to_take > 0:
                self.path.append((current_pos, current_dir))
                try_pos = current_pos + Board.DIRECTIONS[current_dir]
                try_dir = current_dir
                if self.check_oom(try_pos):
                    # we need to use a portal
                    try_pos, try_dir = self.metadata['portals'][tuple(current_pos)]
                    print(current_pos, current_dir, try_pos, try_dir)
                if self.board[tuple(try_pos)] == Tile.WALL:
                    against_wall = True
                else:
                    current_pos, current_dir = try_pos, try_dir
                    steps_to_take -= 1
            
            self._position = current_pos
            self._direction = current_dir
            
        return self._position
    
    @property
    def direction(self):
        return self._direction
    
    @direction.setter
    def direction(self, value):
        """value is L or R"""
        self._direction = Direction((self._direction + {'L': -1, 'R': 1}[value]) % 4)
        return self._direction
    
    
    def follow_single_instruction(self, instruction):
        if instruction in ['R', 'L']:
            self.direction = instruction
        else:
            self.position = int(instruction)
        
    def follow_instructions(self, instructions):
        instruction_list = RE_INSTRUCTION.findall(instructions)
        for ix in tqdm(instruction_list):
            self.follow_single_instruction(ix)
            
    
    def get_pwd(self):
        return 1000 * (self.position[0] + 1) + 4 * (self.position[1] + 1) + self.direction
    
    
    @classmethod
    def from_string(cls, string, **kwargs):
        board_rows = string.split('\n')
        n_rows = len(board_rows)
        n_cols = max(map(len, board_rows))

        board_map = Tile.OOM * np.ones((n_rows, n_cols))

        for idx, l in enumerate(board_rows):
            mo = RE_BOARD_ROW.search(l)
            from_c, to_c = mo.span()
            tiles = mo.group()
            for i, c in enumerate(range(from_c, to_c)):
                board_map[idx, c] = Board.DRAW_REVERSE_MAP[tiles[i]]
                
        return Board(board_map, **kwargs)


    def __str__(self) -> str:
        matrix = self.board.copy()
        for pos in self.metadata['portals']:
            if matrix[pos] != Tile.WALL:
                matrix[pos] = Tile.PORTAL
        
        for pos, d in self.path[-200:]:
            if matrix[tuple(pos)] != Tile.WALL:
                matrix[tuple(pos)] = Tile(d + 4)    
        
        matrix[tuple(self.position)] = Tile.LOC
        vfunc = np.vectorize(lambda x: Board.DRAW_MAP.get(x, "?"))
        environment_array = vfunc(matrix)
        drawing = "\n".join(["".join(row) for row in environment_array.tolist()])
        return drawing


def solve_part1(fp):
    raw = open(fp).read()
    board_string, instructions = raw.split('\n\n')
    
    board = Board.from_string(board_string)
    board.follow_instructions(instructions)
    
    return board.get_pwd()


def solve_part2(fp):
    raw = open(fp).read()
    board_string, instructions = raw.split('\n\n')
    
    test_case = 'test' in fp
    board = Board.from_string(board_string, cube=True, test=test_case)
    board.follow_instructions(instructions)

    open('path.txt', 'w').write(str(board))
    
    return board.get_pwd()


if __name__ == "__main__":
    # print(solve_part1('tests/22.txt'))
    # print(solve_part1('input/22.txt'))
    # print(solve_part2('tests/22.txt'))
    print(solve_part2('input/22.txt'))
