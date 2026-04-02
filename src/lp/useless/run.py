from gurobipy import *
import networkx as nx

def lp(vehicles, G, s, t):
    # LP
    m = Model("Platooning")
    m.setParam("OutputFlag", False)

    # Assoz. array - dict
    x = {}
    y = {}

    for e in G.edges():
        x[e] = {}
        y[e] = m.addVar(vtype=GRB.BINARY, obj=0.1*G[e[0]][e[1]]['c'])
        for h in vehicles:
            x[e][h] = m.addVar(vtype=GRB.CONTINUOUS, lb = 0, obj=0.9*G[e[0]][e[1]]['c'])
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

    #m.setObj()
    m.optimize()


    #Ausgabe
    p = {}
    for h in vehicles:
        succ = {}
        for e in G.edges():
            if x[e][h].X > 0.99:
                succ[e[0]] = e[1]
        p[h] = [s[h]]

        print succ

        while p[h][-1] in succ:
            p[h].append(succ[p[h][-1]])
    return (m.ObjVal, p)
print("runs")


#List
vehicles1 = [1, 2]

s1 = {} #Startknoten
t1 = {} #Zielknoten
s1[1] = 1
t1[1] = 2
s1[2] = 3
t1[2] = 4
G1 = nx.DiGraph()
G1.add_edges_from([(1,2, {'c': 2.99}),(1,5, {'c': 1}),(3,4, {'c': 2.99}),(3,5, {'c': 1}),(5,6, {'c': 1}),(6,2, {'c': 1}),(6,4, {'c': 1})])

(val1, p1) = lp(vehicles1, G1, s1 ,t1)
print "value", val1
for h1 in vehicles1:
    print p1[h1]

