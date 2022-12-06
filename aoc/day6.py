import re
from collections import deque

def find_marker_pos(message, n=4):
    max_number_checks = len(message) - (n - 1)
    for i in range(max_number_checks):
        start_of_package = message[i:i+n]
        if len(set(start_of_package)) == n:
            return i + n

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # First star
    with open('../tests/6.txt') as f:
        for line in f.readlines():
            print(find_marker_pos(line))

    print(find_marker_pos(open('../input/6.txt').read()))

    # Second star
    with open('../tests/6.txt') as f:
        for line in f.readlines():
            print(find_marker_pos(line, n=14))
    print(find_marker_pos(open('../input/6.txt').read(), n=14))