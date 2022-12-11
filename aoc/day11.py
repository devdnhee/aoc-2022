import re
from collections import deque
import logging
import numpy as np
from tqdm import tqdm

RE_START_ITEMS = re.compile(r"Starting items: ((?:\d+,\s)+)")

class Monkey:

    def __init__(self, id=0, items=None, operation=None, test=None, friends=None, worry_level=3):
        self.id = id
        self.items = items
        self.operation = operation
        self.test = test
        self.friends = friends
        self.worry_level = worry_level

    def update(self, test_result, friend):
        self.friends[test_result] = friend

    def throw_item(self):
        item = self.items.popleft()
        # print(f"\tMonkey inspects an item with a worry level of {item}.")
        item = self.operation(item)
        # print(f"\tWorry level -> {item}.")
        item = item // self.worry_level
        # print(f"\tMonkey gets bored with item. Worry level is divided by 3 to {item}.")
        friend = self.friends[not bool(item % self.test)]
        # print(f"\tItem with worry level {item} is thrown to monkey {friend}.")
        return item, friend

    def check_throw(self):
        return len(self.items) > 0

    def receive_item(self, item):
        self.items.append(item)


    @classmethod
    def parse_operation_string(cls, op):
        op = op.strip()
        operation, value = re.search(r'old ([+*]) (\w+)', op).groups()
        if value == 'old':
            return (lambda x: x * x) if operation == '*' else (lambda x: x + x)
        else:
            return (lambda x: x * int(value)) if operation == '*' else (lambda x: x + int(value))

    @classmethod
    def from_string(cls, text, worry_level=3):
        friends = dict()
        init_kwargs = dict()
        for line in text.split('\n'):
            if mo := re.match('^Monkey (\d+):\s?', line):
                init_kwargs["id"] = int(mo.group(1))
                continue
            line = line.strip()
            if line.startswith('Starting items'):
                init_kwargs["items"] = deque(int(match) for match in re.findall('\d+', line))
            elif line.startswith('Operation'):
                init_kwargs["operation"] = Monkey.parse_operation_string(line)
            elif line.startswith('Test'):
                init_kwargs["test"] = int(re.search('(\d+)', line).group(1))
            elif line.startswith('If true'):
                true_friend = int(re.search('(\d+)', line).group(1))
                friends[True] = true_friend
            elif line.startswith('If false'):
                false_friend = int(re.search('(\d+)', line).group(1))
                friends[False] = false_friend
            else:
                raise Exception(f'Unrecognized monkey line: {line}')

        init_kwargs.update({'friends': friends})
        return Monkey(worry_level=worry_level, **init_kwargs)

    def __str__(self):
        return f"Monkey {self.id}, {self.items}, {self.operation},  {self.test}, {self.friends}"


class MonkeyManager:

    def __init__(self, monkeys):
        self.monkeys = monkeys
        self.inspections = {
            idx: 0 for idx, monkey in enumerate(self.monkeys)
        }
        return

    def play_turn(self, monkey_id):
        monkey = self.monkeys[monkey_id]
        while monkey.check_throw():
            self.inspections[monkey_id] += 1
            new_item, receiving_monkey_id = monkey.throw_item()
            self.monkeys[receiving_monkey_id].receive_item(new_item)

    def play_round(self):
        for idx in range(len(self.monkeys)):
            # print(f"Monkey {idx}:")
            self.play_turn(idx)

    def monkey_business(self):
        return np.prod(sorted(self.inspections.values())[-2:])

    @classmethod
    def from_string(cls, text, **kwargs):
        monkey_texts = text.split('\n\n')
        monkeys = [Monkey.from_string(text, **kwargs) for text in monkey_texts]
        return MonkeyManager(monkeys)
        # for monkey_text in enumerate(monkey_texts):

    def __str__(self):
        return '\n'.join([str(monkey) for monkey in self.monkeys])


def simulation(fp, n_rounds=20, worry_level=3):
    text_input = open(fp).read()
    manager = MonkeyManager.from_string(text_input, worry_level=worry_level)
    for _ in tqdm(range(n_rounds)):
        manager.play_round()

    print(f"\n{manager}")
    return manager.monkey_business()

if __name__ == "__main__":
    # print(simulation("../tests/11.txt"))
    print(simulation("../tests/11.txt", worry_level=1, n_rounds=10000))