import re
from collections import deque

RE_MOVE_COMMAND = re.compile("^move (\d+) from (\d+) to (\d+)\s*$")
RE_ITEM = re.compile(r"(\s{3, 4}|\[[A-Z]\])")


def read_file(fp):
    inp = open(fp).read()
    stacks_texts = inp.split("\n\n")[0].rstrip("\n").split("\n")
    commands_texts = inp.split("\n\n")[1].split("\n")

    stack_definition = stacks_texts[-1]
    n_stacks = int(re.search(r"(\d)+$", stack_definition).group(1))

    stacks = [deque() for _ in range(n_stacks)]
    for row in stacks_texts[-2::-1]:
        # items either empty strings or [A-Z]
        items = [row[i : min(i + 4, len(row))] for i in range(0, len(row), 4)]
        items = list(map(lambda x: x.rstrip("] ").lstrip("[ "), items))
        # items = list(map(lambda x: x.rstrip('] ').lstrip('[ '), RE_ITEM.findall(row)))
        for idx, item in enumerate(items):
            if item:
                stacks[idx].append(item)

    commands = [
        tuple(map(int, RE_MOVE_COMMAND.match(text).groups())) for text in commands_texts
    ]
    return stacks, commands


def perform_stack_operations(stacks, commands, one_by_one=True):
    for amount, from_stack_idx, to_stack_idx in commands:
        if one_by_one:
            for _ in range(amount):
                # if len(stacks[from_stack_idx-1]) > 0:
                item = stacks[from_stack_idx - 1].pop()
                stacks[to_stack_idx - 1].append(item)
        else:
            items = [stacks[from_stack_idx - 1].pop() for _ in range(amount)]
            stacks[to_stack_idx - 1].extend(reversed(items))
    return stacks


def stack_supply(fp, one_by_one=True):
    stacks, commands = read_file(fp)
    stacks = perform_stack_operations(stacks, commands, one_by_one)
    answer = "".join([s.pop() if len(stacks) > 0 else " " for s in stacks])
    return answer


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    # First star
    print(stack_supply("../tests/5.txt"))
    # print(stack_supply("../input/5.txt"))

    # Second star
    print(stack_supply("../tests/5.txt", one_by_one=False))
    # print(stack_supply("../input/5.txt", one_by_one=False))
