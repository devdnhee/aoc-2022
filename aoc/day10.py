class CPU:

    NOOP_CYCLES = 1
    ADDX_CYCLES = 2

    def __init__(self):
        # X contains history of all values AFTER the cycle has happened!
        self.X = [1]

    def noop(self):
        self.X.extend(CPU.NOOP_CYCLES * [self.X[-1]])

    def addx(self, v):
        self.X.extend((CPU.ADDX_CYCLES - 1) * [self.X[-1]])
        self.X.append(self.X[-1] + v)

    def run_command(self, command):
        match command.rstrip().split():
            case ["noop"]:
                self.noop()
            case ["addx", v]:
                self.addx(int(v))

    def signal_strength(self, cycle):
        """Calculates signal strength DURING cycle"""
        return self.X[cycle - 1] * cycle

    def draw_crt(self):
        crt_drawing = ""
        # iterate over cycles
        for cycle in range(1, len(self.X)):
            x = self.X[cycle - 1]
            sprite_pos = [x - 1, x, x + 1]
            crt_drawing += "#" if (cycle - 1) % 40 in sprite_pos else "."
            if cycle % 40 == 0:
                crt_drawing += "\n"
        return crt_drawing

    def __str__(self):
        return str(self.X)


def simulation(fp):
    commands = open(fp).readlines()
    cpu = CPU()

    for command in commands:
        cpu.run_command(command)

    requested_cycles = range(20, 221, 40)
    print(cpu.draw_crt())

    return sum(map(cpu.signal_strength, requested_cycles))


if __name__ == "__main__":
    print(simulation("../tests/10a.txt"))
    print(simulation("../input/10.txt"))
