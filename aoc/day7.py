import re

RE_FILE_MATCH = re.compile(r"^(\d+)\s(.+)$")


def read_directory_structure(fp):
    commands = map(lambda l: l.rstrip(), open(fp).readlines())
    directories = {"/": 0}
    current_directory = ""
    for command in commands:
        if command.startswith("$ cd"):
            d = command.split()[-1]
            if d == "/":
                current_directory = "/"
            elif d == "..":
                current_directory = "-".join(current_directory.split("-")[:-1])
            else:
                current_directory = f"{current_directory}-{d}"
            if current_directory not in directories:
                directories[current_directory] = 0
        elif command.startswith("$ ls"):
            continue
        elif command.startswith("dir"):
            d = command.split()[-1]
            listed_directory = f"{current_directory}-{d}"
            if listed_directory not in directories:
                directories[listed_directory] = 0
        elif mo := RE_FILE_MATCH.match(command):
            file_size, file_name = mo.groups()
            walk = current_directory.split("-")
            paths = ["-".join(walk[: i + 1]) for i in range(len(walk))]
            for path in paths:
                directories[path] += int(file_size)
    return directories


def sum_all_directories(fp, threshold=100000):
    d_fs = read_directory_structure(fp)
    return sum([d_fs[k] for k in d_fs if d_fs[k] <= threshold])


def find_dir_to_delete_size(fp, max_space=70000000, space_required=30000000):
    d_fs = read_directory_structure(fp)
    total_size = d_fs["/"]
    max_space_for_update = max_space - space_required
    space_to_delete = total_size - max_space_for_update
    if space_to_delete > 0:
        return min([fs for fs in d_fs.values() if fs > space_to_delete])
    return


if __name__ == "__main__":
    # First star
    print(sum_all_directories("../tests/7.txt"))
    # print(sum_all_directories("../input/7.txt"))

    # Second star
    print(find_dir_to_delete_size("../tests/7.txt"))
    # print(find_dir_to_delete_size("../input/7.txt"))
