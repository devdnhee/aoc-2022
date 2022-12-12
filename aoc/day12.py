import numpy as np
import networkx as nx

def read_as_matrix(fp):
    lines = [l.rstrip() for l in open(fp).readlines()]
    n_rows = len(lines)
    n_cols = len(lines[0])

    matrix = np.zeros((n_rows, n_cols))
    start, end = None, None
    for r, line in enumerate(lines):
        for c, character in enumerate(line):
            if character == 'S':
                matrix[r, c] = 1
                start = (r, c)
                continue
            if character == 'E':
                matrix[r, c] = 26
                end = (r, c)
                continue
            matrix[r, c] = ord(character) - ord('a') + 1
    return matrix, start, end


def get_neigbours(matrix, r, c):
    n_rows, n_cols = matrix.shape
    neighbours_indices = [
        (r, c-1), (r-1, c), (r+1, c), (r, c+1)
    ]
    neighbours = [n for n in neighbours_indices
                  if 0 <= n[0] < n_rows
                    and 0 <= n[1] < n_cols
                    and (matrix[n[0], n[1]] - matrix[r, c] <= 1)]
    return neighbours



def read_hills_as_graph(fp):
    matrix, start, end = read_as_matrix(fp)
    n_rows, n_cols = matrix.shape

    G = nx.DiGraph()
    # add nodes
    for r in range(n_rows):
        for c in range(n_cols):
            G.add_node((r, c))
    # add edges
    for r in range(n_rows):
        for c in range(n_cols):
            neigbours = get_neigbours(matrix, r, c)
            for n in neigbours:
                G.add_edge((r, c), n)

    return G, start, end, matrix


def write_path(fp, matrix, path):
    n_rows, n_cols = matrix.shape
    grid = [n_cols * ["."] for i in range(n_rows)]
    for i in range(len(path) - 1):
        r_from, c_from = path[i][0], path[i][1]
        r_to, c_to = path[i+1][0], path[i+1][1]
        if r_from > r_to:
            grid[r_from][c_from] = 'v'
        if r_from < r_to:
            grid[r_from][c_from] = '^'
        if c_from < c_to:
            grid[r_from][c_from] = '>'
        if c_from > c_to:
            grid[r_from][c_from] = '<'
    s = "\n".join(["\t".join(row) for row in grid])
    with open(fp, 'w') as f:
        f.write(s)

def simulation_part1(fp):
    G, start, end, matrix = read_hills_as_graph(fp)
    shortest_path = nx.shortest_path(G, source=start, target=end)
    # write_path('G.txt', matrix, shortest_path)
    return len(shortest_path) - 1

def simulation_part2(fp):
    G, start, end, matrix = read_hills_as_graph(fp)
    shortest_path_dict = nx.shortest_path(G, source=None, target=end)
    distances = {t: len(shortest_path_dict[t]) - 1 for t in shortest_path_dict if matrix[t[0], t[1]] == 1}
    return min(distances.values())


if __name__ == "__main__":
    print(simulation("../tests/12.txt"))
    print(simulation_part2("../input/12.txt"))
    # print(simulation("../tests/11.txt", ring=True, worry_level=1, n_rounds=10000))
    # print(simulation("../input/11.txt", ring=True, worry_level=1, n_rounds=10000))