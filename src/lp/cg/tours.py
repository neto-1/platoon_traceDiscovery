from gurobipy import *
import networkx as nx

def tour(vehicles, G, tours):
    # LP
    m = Model("tour")
    m.setParam("OutputFlag", True)

    # Assoz. array - dict




    print("optimization modell is complete, optimization prozess can start")
    #m.setObj()
    m.optimize()
    print("----------------")
    print(m.status)
    print(m.Objval)


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
    print("-------------------------------------")

    print("lp ends heree")
    return (m.ObjVal, p, eids)