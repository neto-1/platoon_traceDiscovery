from gurobipy import *
import networkx as nx


def lp(vehicles, graph, s, t, saving):
    # LP
    m = Model("Platooning")
    m.setParam("OutputFlag", False)

    # Association. array - dict
    x = {}
    y = {}

    for e in graph.edges():
        x[e] = {}
        y[e] = m.addVar(vtype=GRB.BINARY, obj=saving*graph[e[0]][e[1]]['c'])
        for h in vehicles:
            x[e][h] = m.addVar(vtype=GRB.CONTINUOUS, lb=0, obj=(1-saving)*graph[e[0]][e[1]]['c'])
    m.update()

    for v in graph.nodes():
        for h in vehicles:
            if v == s[h]:
                b = 1
            elif v == t[h]:
                b = -1
            else:
                b = 0
            m.addConstr(quicksum(x[e][h] for e in graph.out_edges(v)) -
                        quicksum(x[e][h] for e in graph.in_edges(v)) == b)

    for e in graph.edges():
        for h in vehicles:
            m.addConstr(x[e][h] <= y[e])

    # m.setObj()
    m.optimize()

    # print("status : ", m.getAttr(GRB.Attr.Status))
    # output
    p = {}
    eids = {}

    for h in vehicles:
        succ = {}
        succedges = []
        for e in graph.edges():
            if x[e][h].X > 0.99:
                succ[e[0]] = e[1]
                succedges.append(graph[e[0]][e[1]]['id'])
            elif x[e][h].X > 0.01:
                print("ERROR")
                exit(0)
        p[h] = [s[h]]

        eids[h] = succedges

        while p[h][-1] in succ:
            p[h].append(succ[p[h][-1]])

    # optEdges = set()
    # for h in vehicles:
    #     for e in graph.edges():
    #         if x[e][h].X > 0.99:
    #
    #             optEdges.add(graph[e[0]][e[1]]['id'])

    return m.ObjVal, p, eids
