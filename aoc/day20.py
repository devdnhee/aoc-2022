def read_file(fp):
    return [int(l.strip()) for l in open(fp).readlines()]

 
def mixing(to_mix, order):
    mixed = to_mix.copy()
    N = len(order)
    for t in order:
        i = mixed.index(t)
        i_new = (i + t[1]) % (N-1)
        mixed.pop(i)
        mixed.insert(i_new, t)    
    return mixed


def multimixing(lst, decription_key=811589153, N=10):
    order = list(enumerate(map(lambda el: decription_key * el, lst)))
    mix = order.copy()
    for _ in range(N):
        mix = mixing(mix, order)
    return [t[1] for t in mix]
    

def solve_part1(fp):
    lst = list(enumerate(read_file(fp)))
    mixed = [t[1] for t in mixing(lst, lst)]
    N = len(mixed)
    indices = [1000, 2000, 3000]
    i0 = mixed.index(0)
    return sum([mixed[(i0 + pos) % N] for pos in indices])


def solve_part2(fp):
    lst = read_file(fp)
    mixed = multimixing(lst)
    N = len(mixed)
    indices = [1000, 2000, 3000]
    i0 = mixed.index(0)
    return sum([mixed[(i0 + pos) % N] for pos in indices])


if __name__ == '__main__': 
    solve_part1('../tests/20.txt')
    # solve_part1('../input/20.txt')

    solve_part2('../tests/20.txt')
    # solve_part2('../input/20.txt')
