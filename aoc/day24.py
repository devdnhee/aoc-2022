import numpy as np
from enum import IntEnum
from collections import namedtuple
import math
from copy import deepcopy
import sys
sys.setrecursionlimit(2000)

class Direction(IntEnum):
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    UP = 4
    
class Tile(IntEnum):
    CLEAR = 0
    BLIZZARD_RIGHT = 1
    BLIZZARD_DOWN = 2
    BLIZZARD_LEFT = 3
    BLIZZARD_UP = 4
    MULTIPLE = 5
    WALL = 6
    LOC = -1
    
class Basin:
    DRAW_MAP = {
        Tile.CLEAR: '.',
        Tile.BLIZZARD_RIGHT: '>',
        Tile.BLIZZARD_DOWN: 'v',
        Tile.BLIZZARD_LEFT: '<',
        Tile.BLIZZARD_UP: '^',
        Tile.MULTIPLE: 'X',
        Tile.LOC: 'E',
        Tile.WALL: '#'
    }
    DRAW_REVERSE_MAP = {v:k for k, v in DRAW_MAP.items()}
    DIRECTIONS = [
        np.array([0, 0]), # WAIT
        np.array([0, 1]), # RIGHT
        np.array([1, 0]), # DOWN
        np.array([0, -1]), # LEFT
        np.array([-1, 0]), # UP
    ]
    
    def __init__(self, blizzards, end_pos, start_pos=(0, 1)):
        self.pos = start_pos
        self.end_pos = end_pos
        self.state_map = dict()
        self.initialize_environment(blizzards)
        self.time = 0
        
        
    def initialize_environment(self, blizzards):
        n_rows = self.end_pos[0] + 1
        n_cols = self.end_pos[1] + 2
        self.env = np.zeros((n_rows, n_cols))
        self.blizzards = {
           d: np.zeros((n_rows, n_cols)) for d in iter(Direction)
        }
        
        # walls
        self.env[[0, -1], :] = Tile.WALL
        self.env[:, [0, -1]] = Tile.WALL
        
        # blizzards
        for (r, c), d in blizzards:
            self.env[r, c] = 1
            self.blizzards[d][r, c] = 1
               
        # start and end pos
        self.env[self.pos] = Tile.CLEAR
        self.env[self.end_pos] = Tile.CLEAR

        
        # states
        self.state_map[0] = {
            'env': deepcopy(self.env),
            'blizzards': deepcopy(self.blizzards),
            'distance': np.Inf * np.ones((n_rows, n_cols))
        }
        # self.state_map[0]['distance'][self.pos] = 0
        
        # lcm
        self.lcm = math.lcm(n_rows-2, n_cols-2)
        
        
    def restore(self, time):
        self.env = self.state_map[time % self.lcm]['env']
        self.blizzards = self.state_map[time % self.lcm]['blizzards']
        self.time = time
        
        
    def store(self):
        self.state_map[self.time] = dict(
            env=deepcopy(self.env), blizzards = deepcopy(self.blizzards)
        )
        
    
    def initialize_distances(self):
        # initialize distances
        n_rows, n_cols = self.env.shape
        for t in range(self.lcm):
            self.state_map[t]['distance'] = np.Inf * np.ones((n_rows, n_cols))    
        
    
    def initialize_states_and_restore(self):
        for t in range(1, self.lcm):
            self.time += 1
            self.shift_blizzards()
            self.update_environment()
            self.store()
            # self.state_map[t]['distance'][self.pos] = 0
        self.restore(0)
        
        
    def shift_blizzards(self):
        n_rows, n_cols = self.env.shape
        self.blizzards[Direction.RIGHT] = self.blizzards[Direction.RIGHT][:, [0, -2] + list(range(1, n_cols-2)) + [-1]]
        self.blizzards[Direction.DOWN] = self.blizzards[Direction.DOWN][[0, -2] + list(range(1, n_rows-2)) + [-1], :]
        self.blizzards[Direction.LEFT] = self.blizzards[Direction.LEFT][:, [0] + list(range(2, n_cols-1)) + [1, -1]]
        self.blizzards[Direction.UP] = self.blizzards[Direction.UP][[0] + list(range(2, n_rows-1)) + [1, -1], :]
        
        
    def update_environment(self):
        self.env = np.where(self.env==Tile.WALL, Tile.WALL, 0) + self.blizzards[Direction.RIGHT] + self.blizzards[Direction.DOWN] \
            + self.blizzards[Direction.LEFT] + self.blizzards[Direction.UP]
            
    
    def step(self, direction):
        self.time += 1
        if self.time not in self.state_map:
            self.shift_blizzards()
            self.update_environment()
        else:
            self.restore(self.time)
        self.pos = tuple(np.array(self.pos) + direction)
        
    
    def check_valid(self, pos, t):
        if pos[0] < 0 or pos[0] >= self.env.shape[0] or pos[1] < 0 or pos[1] >= self.env.shape[1]:
            return False
        return self.state_map[t % self.lcm]['env'][pos] <= 0
        
        
    def options(self, pos=None, t=None, sort=-1):
        if pos is None:
            pos = self.pos
        if t is None:
            t = self.time
        positions = ((d, tuple(np.array(pos) + d)) for d in Basin.DIRECTIONS)
        valid = [(d, p) for d, p in positions if self.check_valid(p, t+1)]
        return list(sorted(valid, key=lambda t: -sort*(t[1][0]**2 + t[1][1]**2)))
    
    
    def find_shortest_path(self, t=0, max_depth=1500, pos=None, target=None, sort=-1):
        if pos is None:
            pos = self.pos
            
        if target is None:
            target = self.end_pos
            
        if pos == target:
            return [pos], t
        
        if t >= max_depth:
            return [pos], np.Inf
        
        if t >= self.state_map[t % self.lcm]['distance'][pos]:
            return [pos], np.Inf
        
        self.state_map[t % self.lcm]['distance'][pos] = t
        
        best_path, best_time = None, np.Inf
        options = self.options(pos, t, sort=sort)
        for d, new_pos in options:
            path, time = self.find_shortest_path(t=t+1, pos=new_pos, target=target)
            if time < best_time:
                best_path, best_time = [pos] + path, time
        
        return best_path, best_time
        
        

    def __str__(self):
        matrix = self.env
        matrix = np.where((matrix > 1) & (matrix <=4), Tile.MULTIPLE, matrix)
        for d, blizz in self.blizzards.items():
            matrix = np.where((matrix == 1) & (blizz == 1), Tile(d), matrix)
        matrix[self.pos] = Tile.LOC
        
        vfunc = np.vectorize(lambda x: Basin.DRAW_MAP.get(x, "?"))
        environment_array = vfunc(matrix)
        drawing = "\n".join(["".join(row) for row in environment_array.tolist()])
        return drawing
    

    @classmethod
    def from_string(cls, string):
        lines = string.split('\n')
        blizzards = []
        for row, line in enumerate(lines):
            new_blizzards = [((row, col), Direction(Basin.DRAW_REVERSE_MAP[el])) 
                             for col, el in enumerate(line) if el in '<>^v']
            blizzards.extend(new_blizzards)
        
        end_pos = (len(lines) - 1, lines[-1].index('.'))

        return Basin(blizzards, end_pos=end_pos)
    

def solve_part1(fp):
    raw = open(fp).read().strip()
    b = Basin.from_string(raw)
    b.initialize_states_and_restore()
    b.initialize_distances()
    _, time = b.find_shortest_path()
    return time


def solve_part2(fp):
    raw = open(fp).read().strip()
    b = Basin.from_string(raw)
    b.initialize_states_and_restore()
    
    _, time1 = b.find_shortest_path()
    b.initialize_distances()
    _, time2 = b.find_shortest_path(t=time1, pos=b.end_pos, target=(0, 1), max_depth=1000, sort=1)
    b.initialize_distances()
    _, time3 = b.find_shortest_path(t=time2)
    
    return time3


if __name__ == '__main__':
    print(solve_part1('tests/24.txt'))
    print(solve_part1('input/24.txt'))
    print(solve_part2('tests/24.txt'))

