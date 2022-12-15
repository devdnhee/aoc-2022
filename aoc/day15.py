import re
from tqdm import tqdm


def parse_input(fp):
    raw_input = open(fp).read()
    numbers = [int(n) for n in re.findall(r"-?\d+", raw_input)]
    pairs = [
        (complex(numbers[i], numbers[i + 1]), complex(numbers[i + 2], numbers[i + 3]))
        for i in range(0, len(numbers), 4)
    ]
    return pairs


def manhattan_distance(a, b):
    return abs(a.real - b.real) + abs(a.imag - b.imag)


def no_beacons_y(sensor, closest_beacon, y):
    distance = manhattan_distance(sensor, closest_beacon)
    y_diff = abs(sensor.imag - y)
    if y_diff > distance:
        return None

    y_center = complex(sensor.real, y)
    x_dev = distance - y_diff
    y_range = (y_center - x_dev, y_center + x_dev)
    return y_range


def merge_intervals(intervals):
    intervals = sorted(
        filter(lambda i: i is not None, intervals), key=lambda c: c[0].real
    )
    # intervals = map(lambda t: (t[0].real, t[1].real), intervals)
    merged = []
    current = intervals[0]
    for i in range(1, len(intervals)):
        if (
            current[1].real >= intervals[i][0].real
            and intervals[i][1].real >= current[1].real
        ):
            # partly overlap detected, change current pointer
            current = (current[0], intervals[i][1])
        elif current[1].real < intervals[i][0].real:
            merged.append(current)
            current = intervals[i]
    merged.append(current)
    return merged


def find_n_beacons_in_square(beacons, c1, c2):
    intersect = set(
        b
        for b in beacons
        if c1.real <= b.real <= c2.real and c2.imag <= b.imag <= c2.imag
    )
    return len(intersect)


def count_no_beacons(fp, y):
    pairs = parse_input(fp)
    sensors = [p[0] for p in pairs]
    beacons = [p[1] for p in pairs]
    no_beacons_ranges = [no_beacons_y(s, b, y) for s, b in pairs]
    merged = merge_intervals(no_beacons_ranges)
    return sum(
        [
            manhattan_distance(*interval)
            + 1
            - find_n_beacons_in_square(beacons, *interval)
            for interval in merged
        ]
    )


def bound_interval(i, xmin=0, xmax=20, ymin=0, ymax=20):
    return complex(max(xmin, i[0].real), max(ymin, i[0].imag)), complex(
        min(xmax, i[1].real), min(ymax, i[1].imag)
    )


def find_beacons_brute_force(sensors, beacons, min_pos=0, max_pos=20):
    for y in tqdm(range(min_pos, max_pos)):
        intervals = [no_beacons_y(s, b, y) for s, b in zip(sensors, beacons)]
        # bound intervals to search range
        intervals = [
            bound_interval(i, min_pos, max_pos, min_pos, max_pos)
            for i in intervals
            if i is not None
        ]
        merged = merge_intervals(intervals)
        if len(merged) > 1:
            pos = merged[0][1] + 1
            print(f"FOUND POSITION: {merged} -> {pos}")
            return pos
    return None


def tuning_frequency(fp, min_pos=0, max_pos=20):
    pairs = parse_input(fp)
    sensors = [p[0] for p in pairs]
    beacons = [p[1] for p in pairs]
    position = find_beacons_brute_force(sensors, beacons, min_pos, max_pos)
    return 4000000 * position.real + position.imag


if __name__ == "__main__":
    print(count_no_beacons("../tests/15.txt", y=10))
    print(count_no_beacons("../input/15.txt", y=2000000))
    print(tuning_frequency("../tests/15.txt"))
    print(tuning_frequency("../input/15.txt", max_pos=4000000))
