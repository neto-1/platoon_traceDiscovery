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


def getGroups(x):
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
    """length of x is a number of nodes in graph"""
    # max(x) < len(x)
    #x = [0,1,1,3]
    # x = [0,1,2,3]
    # #x = [0,1,0,1]
    # inf = len(x)#float('inf')
    # #print(len(x))
    # weight = [[0, 0.1, -inf, 0.9], # node 0
    #           [0.1, 0, 0.8, 0.2], # node 1
    #           [-inf, 0.8, 0, -inf], # node 2
    #           [0.9, 0.2, -inf, 0]] # node 3
    #
    #
    # x = [0,1,2,3,4,5]
    # weight = [[0, 0.9, 0.9, 1, -4, -4], # node 0
    #           [0.9, 0, 0.9, -4, -4, -4], # node 1
    #           [0.9, 0.9, 0, -4, -4, -4], # node 2
    #           [1, -4, -4, 0, 0.9, 0.9], # node 3
    #           [-4, -4, -4, 0.9, 0, 0.9], # node 4
    #           [-4, -4, -4, 0.9, 0.9, 0] # node 5
    #           ]
    #
    # weight = [[0, 0.3, 0.3, 1, -4, -4], # node 0
    #           [0.3, 0, 0.3, -4, -4, -4], # node 1
    #           [0.3, 0.3, 0, -4, -4, -4], # node 2
    #           [1, -4, -4, 0, 0.1, 0.3], # node 3
    #           [-4, -4, -4, 0.1, 0, 0.311], # node 4
    #           [-4, -4, -4, 0.3, 0.311, 0] # node 5
    #           ]

    """
    csolver = CliqueSolver(weight)
    sc = csolver.calcSC(x)
    #print DataFrame(sc)
    #print x
    print(weight)
    x, f, sc, k_best = csolver.SGVNS(x, 1, 0, 0, 0)
    print "x: " + str(x) + " f: " + str(f)
    
    print k_best
    
    """


    #f = csolver.calcF(x)
    #x, sc, f = csolver.LSInsert(x, sc, f)
    #print x


    #x_b = [0,1,0,1]
    #x_b = [1,1,2,3]
    #x_n = [1,1,1,1]
    #csolver.d(x_b,x_n)


    # """ Large negative M number"""
    # M = -10
    #
    # """ Weighted Graph """
    # weight = [[0, 0.3, 0.3, 1, M, M], # node 0
    #           [0.3, 0, 0.3, M, M, M], # node 1
    #           [0.3, 0.3, 0, M, M, M], # node 2
    #           [1, M, M, 0, 0.1, 0.3], # node 3
    #           [M, M, M, 0.1, 0, 0.311], # node 4
    #           [M, M, M, 0.3, 0.311, 0] # node 5
    #           ]
    #
    #
    #

    # M = 0
    #
    # weight = [[0, 0.9, 0.2, M], # node 0
    #           [0.9, 0, 0.1, 0.1], # node 1
    #           [0.2, 0.1, 0, 0.9], # node 2
    #           [M, 0.1, 0.9, 0], # node 3
    #           ]
    #
    # """ Start trivial groups """
    # x = [i for i in range(len(weight))]
    #
    # #print x
    # print(weight)
    #
    # print(x)
    #
    #
    #
    # M = 0
    #
    # weight = [[0, 0.9, 0.2, M], # node 0
    #           [0.9, 0, 0.1, 0.1], # node 1
    #           [0.2, 0.1, 0, 0.9], # node 2
    #           [M, 0.1, 0.9, 0], # node 3
    #           ]
    #
    # i_m = IM(weight)
    #
    # cgreedy = GreedyCPP(i_m)
    # x = cgreedy.find_initial_solution()
    #
    #
    #
    #
    # print (x)
    #
    # print (weight)
    #
    # M = 0
    #
    # weight = [[0, 0.9, 0.2, M], # node 0
    #           [0.9, 0, 0.1, 0.1], # node 1
    #           [0.2, 0.1, 0, 0.9], # node 2
    #           [M, 0.1, 0.9, 0], # node 3
    #           ]
    #
    # csolver = NHoodCPP(i_m)
    # x, f, sc, k_best = csolver.SGVNS(x, 1, 0, 0, 0)
    #
    #
    #
    # print (x)


    """
    visual_style = {}
    #visual_style["edge_width"] = g.es["weight"]
    visual_style["vertex_label"] = [v.index for v in g.vs] #for v in g.vs:
    layout = g.layout("kk")
    
    plot(g,  **visual_style)
    """

    #plot(g,  **visual_style)

    """
    print(g)
    print(g.is_weighted())
    print(g.get_adjacency(attribute='weight'))
    print(g.maximal_cliques(min=0, max=0))
    print(g.es["weight"])
    """

    print (sys.version)

    # length = 8
    # x = (0,)
    # for i in range(1, length):
    #     x += (i,)
    #
    # print x
    # exit()
    #
    # weight = [[0, 1, 1, 1], # node 0
    #           [1, 0, 1, 1], # node 1
    #           [1, 1, 0, 1], # node 2
    #           [1, 1, 1, 1], # node 3
    #           ]

    #i_m = IM(weight)



    i_m = DB.get_incentive_matrix("")

    tr = TrivialCPP(i_m)
    inittrivial = tr.find_initial_solution()

    #print str(inittrivial) + " trivial"

    cgreedy = GreedyCPP(i_m)
    initgreedy = cgreedy.find_initial_solution()

    random = RandomCPP(i_m)
    initrandom = random.find_initial_solution()

    #print " random: " + str(initrandom)
    #print " random groups: " + str(getGroups(initrandom))

    start = time.time()

    #x = [6,6,6,6,6,6,6]
    csolver = NHoodCPP(i_m)
    x, f, sc, k_best, local_min, local_max_f, function_value = csolver.SGVNS(inittrivial, 0.5, 0, 0, 0)

    print "trivial f: " + str(csolver.calcF(inittrivial))
    print "greedy f: " + str(csolver.calcF(initgreedy))
    print "random f: " + str(csolver.calcF(initrandom))

    print "trivial sgvns f: " + str(f)


    #print "sgvns x: " + str(x)
    # print k_best
    # print("------")
    all_groups = set()
    for solution, objective in k_best:
        next_groups = set(getGroups(solution))
        all_groups = all_groups.union(next_groups)
    # print(all_groups)

    #print str(csolver.calcF(initgreedy)) + " " + str(initgreedy) + " greedy"
    #print str(len(Counter(x))) + str(x) + " nhood"
    #print function_value

    end = time.time()
    print("time: " + str(end - start))

    plt.plot(function_value)
    plt.show()



    g = Graph()
    g = g.Weighted_Adjacency(i_m.get_matrix_copy(), mode=ADJ_UNDIRECTED, attr="weight", loops=False)

    visual_style = {}
    visual_style["edge_width"] = g.es["weight"]
    #visual_style["vertex_label"] = [v.index for v in g.vs]  # for v in g.vs:
    visual_style["vertex_label"] = x  # for v in g.vs:
    layout = g.layout("kk")

    #g.vs["label"] = [24, 22, 17, 2, 2, 2, 17, 17, 14, 15, 15, 7, 0, 25, 25, 15, 14, 20, 18, 22, 25, 24, 7, 14, 16, 24, 26]
        #= g.vs["name"]
    #print g.es["label"]

    plot(g, **visual_style)

    ################
    # Q1 Helper Class for Matrix checking
    # 02 Inheritance of classes

    """ 
        Solution Space 
    """

    #print local_min

    #print local_max_f

    # sgraph = SolutionGraph(local_min, csolver)
    # sgraph.graph_constuction()


if __name__ == "__main__":
    main()
