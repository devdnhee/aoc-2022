import numpy as np
import re

def read_field(fp):
    lines = open(fp).readlines()
    height = len(lines)
    width = len(lines[0].strip('\n '))
    field = np.zeros((height, width))

    for row, line in enumerate(lines):
        field[row] = re.findall('\d', line)

    return field

def get_min_allowed_height(field, r, c):
    min_left = field[r, :c].max() + 1
    min_right = field[r, c+1:].max() + 1
    min_top = field[:r, c].max() + 1
    min_bottom = field[r+1:, c].max() + 1
    return min(min_left, min_right, min_bottom, min_top)


def scenic_score(field, r, c):
    idx_left = np.argwhere(field[r, c-1::-1] >= field[r, c])
    view_left = idx_left.min() + 1 if len(idx_left) > 0 else c

    idx_right = np.argwhere(field[r, c+1:] >= field[r, c])
    view_right = idx_right.min() + 1 if len(idx_right) > 0 else field.shape[1] - c - 1

    idx_top = np.argwhere(field[r-1::-1, c] >= field[r, c])
    view_top = idx_top.min() + 1 if len(idx_top) > 0 else r

    idx_bottom = np.argwhere(field[r+1:, c] >= field[r, c])
    view_bottom = idx_bottom.min() + 1 if len(idx_bottom) > 0 else field.shape[0] - r - 1

    return view_left * view_right * view_top * view_bottom

def count_visible_trees(fp):
    field = read_field(fp)
    height, width = field.shape

    min_height = np.zeros(field.shape)
    scenic_scores = np.zeros(field.shape)
    for r in range(1, height-1):
        for c in range(1, width-1):
            min_height[r, c] = get_min_allowed_height(field, r, c)
            scenic_scores[r, c] = scenic_score(field, r, c)

    visible = field >= min_height

    return visible.sum(), scenic_scores.max()


if __name__ == '__main__':
    print(count_visible_trees('../tests/8.txt'))
    print(count_visible_trees('../input/8.txt'))