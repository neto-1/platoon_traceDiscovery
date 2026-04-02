from GreedyCPP import GreedyCPP
from TrivialCPP import TrivialCPP
from NHoodCPP import NHoodCPP
from RandomCPP import RandomCPP
from IM import IM
from DB import DB
from SolutionGraph import SolutionGraph
from igraph import *
import copy
from collections import Counter
import matplotlib.pyplot as plt
import sys
import time
import json
from networkx.readwrite import json_graph


def get_groups(x):
    group_num = max(x)+1
    groups = [0 for i in range(group_num)]
    for i in range(len(x)):
        if groups[x[i]] == 0:
            groups[x[i]] = (i,)
        else:
            groups[x[i]] += (i,)
    l = len(groups)-1
    for i in range(l, 0, -1):
        if groups[i] == 0:
            del groups[i]
    return groups


def main():
    incentive_matrix = DB.get_incentive_matrix("")

    tr = TrivialCPP(incentive_matrix)
    inittrivial = tr.find_initial_solution()

    # cgreedy = GreedyCPP(incentive_matrix)
    # initgreedy = cgreedy.find_initial_solution()

    # random = RandomCPP(incentive_matrix)
    # initrandom = random.find_initial_solution()

    start = time.time()

    csolver = NHoodCPP(incentive_matrix)
    x, f, sc, k_best, local_min, local_max_f, function_value = csolver.SGVNS(inittrivial, 0.5, 0, 0, 0)

    all_groups = set()
    for solution, objective in k_best:
        next_groups = set(get_groups(solution))
        all_groups = all_groups.union(next_groups)

    end = time.time()
    print("time: " + str(end - start))

    DB.store_groups(all_groups)

if __name__ == "__main__":
    main()

    output_data = {
        'times': {
            'calc_group_savings': 0,  # time to calculate all group savings
            'determine_disjunct_groups': 0,  # time to determine the disjoint groups
            'routing': 0,  # complete time of calculating the savings of all created groups
            'storing_routes': 0 # the time to store all platooning routes of the respectively groups
        }
    }

print(json.dumps(output_data))
