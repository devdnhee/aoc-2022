snafu_map = {
    '-': -1,
    '=': -2,
}

def snafu_to_decimal(snafu):
    return sum(int(snafu_map.get(c, c))*5**p for p, c in enumerate(reversed(snafu)))
    

def decimal_to_snafu(decimal):
    """2=-1=0 for 4890"""
    snafu = ''
    pow = 0
    while decimal > 0:
        # print(decimal)
        modulo = decimal % 5
        if modulo == 3:
            c = '='
            modulo = -2
        elif modulo == 4:
            c = '-'
            modulo = -1
        else:
            c = str(modulo)
        snafu = c + snafu
        decimal = (decimal - modulo) // 5
        pow += 1
    return snafu


def solve_part1(fp):
    inp = open(fp).read().strip().split('\n')
    decimal_sum = sum(list(map(snafu_to_decimal, inp)))
    return decimal_to_snafu(decimal_sum)

if __name__ == '__main__':
    print(solve_part1('tests/25.txt'))
    