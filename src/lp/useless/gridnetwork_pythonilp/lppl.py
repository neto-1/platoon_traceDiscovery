from gurobipy import *
import networkx as nx


def lp(vehicles, G, s, t, saving):

    # LP
    m = Model("Platooning")
    m.setParam("OutputFlag", False)

    # Assoz. array - dict
    x = {}
    y = {}
    for e in G.edges():
        x[e] = {}
        y[e] = m.addVar(vtype=GRB.BINARY, obj=saving*G[e[0]][e[1]]['c'])
        for h in vehicles:
            x[e][h] = m.addVar(vtype=GRB.CONTINUOUS, lb=0, obj=(1-saving)*G[e[0]][e[1]]['c'])
    m.update()

    for v in G.nodes():
        for h in vehicles:
            if v == s[h]:
                b = 1
            elif v == t[h]:
                b = -1
            else:
                b = 0
            m.addConstr(quicksum(x[e][h] for e in G.out_edges(v)) - quicksum(x[e][h] for e in G.in_edges(v)) == b)

    for e in G.edges():
        for h in vehicles:
            m.addConstr(x[e][h] <= y[e])

    # m.setObj()
    m.optimize()

    #print("status : ", m.getAttr(GRB.Attr.Status))
    #Ausgabe
    p = {}
    eids = {}

    for h in vehicles:
        succ = {}
        succedges = []
        for e in G.edges():
            if x[e][h].X > 0.99:
                succ[e[0]] = e[1]
                succedges.append ( G[e[0]][e[1]]['id'] )
            elif x[e][h].X > 0.01:
                print("ERROR")
                exit(0)
        p[h] = [s[h]]

        eids[h] = succedges

        while p[h][-1] in succ:
            p[h].append(succ[p[h][-1]])

    return m.ObjVal, p, eids