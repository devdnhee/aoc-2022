import numpy as np
import pandas as pd

DROPLET = -1
# EXPOSED = 2
OPEN = 0

DRAW_MAP = {
    DROPLET: "#",
    OPEN: ".",
}


def all_sides(x, y, z):
    return [
        (x + 1, y, z),
        (x - 1, y, z),
        (x, y + 1, z),
        (x, y - 1, z),
        (x, y, z + 1),
        (x, y, z - 1),
    ]


def build_np_cube(df):
    """Builds a numpy 3D array that represents the lava droplets and expositions"""
    max_xyz, min_xyz = df.max(), df.min()
    # + 3 to also include edge space to count
    shape = (
        (max_xyz.x - min_xyz.x + 3),
        (max_xyz.y - min_xyz.y + 3),
        (max_xyz.z - min_xyz.z + 3),
    )

    def coord_transform(x, y, z):
        """transforms to the coords in numpy"""
        return x - min_xyz.x + 1, y - min_xyz.y + 1, z - min_xyz.z + 1

    cube = np.zeros(shape)
    for _, x, y, z in df.itertuples():
        x_tf, y_tf, z_tf = coord_transform(x, y, z)
        cube[x_tf, y_tf, z_tf] = DROPLET
        for x_e, y_e, z_e in all_sides(x_tf, y_tf, z_tf):
            if cube[x_e, y_e, z_e] >= 0:
                cube[x_e, y_e, z_e] = cube[x_e, y_e, z_e] + 1

    return cube


def draw_map(map):
    vfunc = np.vectorize(lambda x: DRAW_MAP.get(x, "o"))
    environment_array = vfunc(map)
    drawing = "\n".join(["".join(row) for row in environment_array.tolist()])
    return drawing


def print_cube(cube):
    for i in range(cube.shape[0]):
        print(f"{draw_map(cube[i])}\n\n")


def is_valid(arr, x, y, z):
    x_max, y_max, z_max = arr.shape
    return 0 <= x < x_max and 0 <= y < y_max and 0 <= z < z_max


def bfs_visit(cube, visited, x=0, y=0, z=0, depth=0):
    """Breadth first visit of all nodes.

    The strategy is to start from an edge node (which are either OPEN or EXPOSED).
    Then we try to visit all nodes.
    If nodes are not visited, the counter remains 0.
    """
    unvisited_neighbours = list(
        filter(
            lambda t: is_valid(cube, *t) and visited[t] == 0 and cube[t] >= 0,
            all_sides(x, y, z),
        )
    )
    for xv, yv, zv in unvisited_neighbours:
        visited[xv, yv, zv] = depth
    for xv, yv, zv in unvisited_neighbours:
        bfs_visit(cube, visited, xv, yv, zv, depth + 1)


def solve_part1(fp):
    df = pd.read_csv(fp, names=list("xyz"))
    cube = build_np_cube(df)
    return cube[cube > 0].sum()


def solve_part2(fp):
    df = pd.read_csv(fp, names=list("xyz"))
    cube = build_np_cube(df)

    visited_nodes = np.zeros_like(cube)
    bfs_visit(cube, visited_nodes)

    return cube[(cube > 0) & (visited_nodes > 0)].sum()


if __name__ == "__main__":
    print(solve_part1("tests/18.txt"))
    print(solve_part2("tests/18.txt"))
