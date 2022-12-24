import re
from sympy import symbols, solve, Eq

RE_OPERATION = re.compile('^([a-z]{4}): ([a-z]{4}) ([+-/*]) ([a-z]{4})\s?$')
RE_RESULT = re.compile('^([a-z]{4}): (\d+)\s?$')


def read_input(fp):
    lines = open(fp).readlines()
    results_dict = dict()
    for l in lines:
        if mo := RE_OPERATION.match(l):
            monkey, monkey1, operation, monkey2 = mo.groups()
            results_dict[monkey] = dict(
                operation = (monkey1, operation, monkey2),
                result = None,
            )
            
        elif mo := RE_RESULT.match(l):
            monkey, result = mo.groups()
            results_dict[monkey] = dict(
                operation = None,
                result = int(result),
            )     
    
    return results_dict


def monkey_result(name, results_dict):
    result = results_dict[name]['result']
    if result is not None:
        return result
    
    name1, op, name2 = results_dict[name]['operation']
    if op == '*':
        res = monkey_result(name1, results_dict) * monkey_result(name2, results_dict)
    elif op == '+':
        res = monkey_result(name1, results_dict) + monkey_result(name2, results_dict)
    elif op == '/':
        res = monkey_result(name1, results_dict) / monkey_result(name2, results_dict)
    elif op == '-':
        res = monkey_result(name1, results_dict) - monkey_result(name2, results_dict)
    elif op == '=':
        res = Eq(monkey_result(name1, results_dict) - monkey_result(name2, results_dict), 0)
    
    results_dict[name]['result'] = res
    return res


def solve_part1(fp):
    results_dict = read_input(fp)
    return monkey_result('root', results_dict)


def solve_part2(fp):
    results_dict = read_input(fp)
    results_dict['root']['operation'] = results_dict['root']['operation'][0], '=', results_dict['root']['operation'][2]
    results_dict['humn']['result'] = symbols('x')
    eq = monkey_result('root', results_dict)
    print(eq)
    return solve(eq)

if __name__ == '__main__':
    print(solve_part1('tests/21.txt'))
    print(solve_part2('tests/21.txt'))
    