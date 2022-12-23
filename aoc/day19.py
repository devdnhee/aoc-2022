from enum import IntEnum
import numpy as np
import re
from tqdm import tqdm

class Mineral(IntEnum):
    ORE = 0
    CLAY = 1
    OBSIDIAN = 2
    GEODE = 3

def read_blueprint(line):
    blueprint = np.zeros((4, 3))
    prices = list(map(int, re.findall("\d+", line)))
    indices = [(0, 0), (1, 0), (2, 0), (2, 1), (3, 0), (3, 2)]
    for price, idx in zip(prices[1:], indices):
        blueprint[idx] = price
    return prices[0], blueprint


def np_array_one(shape, idx):
    arr = np.zeros(shape)
    arr[idx] = 1
    return arr


def pruning_options(bank, blueprint, production, t):
    ## which bots can we build
    bots = np.all(bank[:3] >= blueprint, axis=1)
    
    if not np.any(bots):
        return [np.zeros(4)]
    
    if bots[Mineral.GEODE]:
        # if you can buy a geode bot, it's your best option
        return [np_array_one(4, Mineral.GEODE)]
    
    ## which resources should we stop harvesting because saturated
    saturated_rate = np.all(production[:3] >= blueprint, axis=0)
    saturated_time = np.all(bank[:3] + production[:3] * t >= blueprint[Mineral.CLAY:] * t, axis=0)
    
    options = [np.zeros(4)] + [np_array_one(4, i) for i in range(4) 
                               if bots[i] and not saturated_rate[i] and not saturated_time[i]]
    
    # we reverse the options, since depth first we first want to explore the most promising ones
    return list(reversed(options))
 
 
def get_cost(blueprint, option):
    return np.concatenate((blueprint[np.broadcast_to(option, (3, 4)).T == 1], [0]))


def maximize_geodes(blueprint, bank, production, new_bots, t, stats):
    if t == 1:
        bank = bank + production + new_bots
        if bank[Mineral.GEODE] > stats['G']:
            stats['G'] = bank[Mineral.GEODE]
        return bank[Mineral.GEODE], [new_bots]
    
    production = production + new_bots
    
    # Most optimistic upper bound of Geodes to harvest: 1 additional geode bot every turn
    # if the most optimistic is less than best yet -> quit path
    upper_bound = bank[Mineral.GEODE] + t * production[Mineral.GEODE] + t * (t - 1) / 2
    if stats['G'] > upper_bound:
        return bank[Mineral.GEODE], [new_bots]
    
    if t in stats:
        ## Here we quit the path if it can impossibly beat the best so far
        if np.all(bank <= stats[t]['bank']) and np.all(production <= stats[t]['production']):
            # Less stock + less robots for each resource
            return bank[Mineral.GEODE], [new_bots]
        if production[Mineral.GEODE] < stats[t]['production'][Mineral.GEODE] and bank[Mineral.GEODE] < stats[t]['bank'][Mineral.GEODE]:
            # Less Geodes and less geode bots
            return bank[Mineral.GEODE], [new_bots]
        if production[Mineral.GEODE] < stats[t]['production'][Mineral.GEODE] and production[Mineral.OBSIDIAN] < stats[t]['bank'][Mineral.OBSIDIAN]:
            # less geode bots and less obsidian bots than stock of best path (i.e. closer to new geode bot)
            return bank[Mineral.GEODE], [new_bots]
        if bank[Mineral.GEODE] == 0 and production[Mineral.OBSIDIAN] < stats[t]['production'][Mineral.OBSIDIAN] and production[Mineral.CLAY] < stats[t]['production'][Mineral.CLAY]:
            # no geodes and less clay and obsidian bots
            return bank[Mineral.GEODE], [new_bots]
        if np.all(bank + t*production < stats[t]['bank'] + t * stats[t]['production']):
            # interesting heuristic: resource fitness state = bank + t * bots, if it's less for all resources quit the path!
            return bank[Mineral.GEODE], [new_bots]
    
    # get options
    options = pruning_options(bank, blueprint, production, t)

    geodes = [
        maximize_geodes(blueprint, bank - get_cost(blueprint, option) + production, production, option, t - 1, stats) 
        for option in options
    ]
    max_geode, best_option = max(geodes, key=lambda t: t[0])
    
    if max_geode == stats['G']:
        # store the best state seen so far
        stats[t] = dict()
        stats[t]['bank'] = bank
        stats[t]['production'] = production
    
    return max_geode, [new_bots] + best_option


def simulate(blueprint, bank, production, new_bots, t):
    production = production + new_bots
    options = pruning_options(bank, blueprint, production, t)
    bank = bank + production
    return options, bank, production


def max_geode_blueprint(blueprint, t=24):
    # how much do we have from each resource? 
    bank = np.zeros(4)

    # how much are we producing from each resource? equals the amount of robots for each resource
    production = np.array([1, 0, 0, 0])

    # which bots are under construction
    new_bots = np.zeros(4)
    
    stats = dict(G=0)
    max_geode, _ = maximize_geodes(blueprint, bank, production, new_bots, t=t, stats=stats)
    
    return max_geode


def solve_part1(fp, t=24):
    lines = open(fp).readlines()
    quality_levels = []
    for l in tqdm(lines):
        id, blueprint = read_blueprint(l)
        quality = id * max_geode_blueprint(blueprint, t)
        quality_levels.append(quality)
    return sum(quality_levels)


def solve_part2(fp, t=32):
    lines = open(fp).readlines()
    lines = lines[:min(3, len(lines))]
    geodes = []
    for l in tqdm(lines):
        _, blueprint = read_blueprint(l)
        nbr_geodes = max_geode_blueprint(blueprint, t=t)
        geodes.append(nbr_geodes)
    return np.prod(geodes)

if __name__ == '__main__':
    print(solve_part1('tests/19.txt'))
    print(solve_part2('tests/19.txt'))
