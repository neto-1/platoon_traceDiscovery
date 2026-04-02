from gurobipy import *
import networkx as nx


def lp(vehicles, graph, s, t, saving):
    # LP
    m = Model("Platooning")
    m.setParam("OutputFlag", False)

    # Assoz. array - dict
    x = {}  # vehicle uses an edge
    y = {}  # cost of an edge
    ti = {}  # time vehicle uses an edge
    ph = {}  # two vehicles drive over the same edge in the same time
    z = {}  # helping binary variable for constraint 18 and 19
    alpha = {}  # leading vehicle constraint

    # creating the "big number" B for the time contraints
    # big_m = 99999;  # this should be 2*N* sumof(all edge weights) but i should work with a very big number
    big_m = 2 * len(vehicles) * quicksum(graph[e[0]][e[1]]['c'] for e in graph.edges())

    for e in graph.edges():
        x[e] = {}
        ti[e] = {}
        alpha[e] = {}
        ph[e] = {}
        z[e] = {}
        y[e] = {}
        # objective function, see 5 in "the vehicle platooning problem - appendix B"
        # y[e] = m.addVar(vtype=GRB.CONTINUOUS, lb=0, obj=graph[e[0]][e[1]]['c'])
        for h in vehicles:
            y[e][h] = m.addVar(vtype=GRB.CONTINUOUS, lb=0, obj=graph[e[0]][e[1]]['c'])
            ph[e][h] = {}
            z[e][h] = {}
            x[e][h] = m.addVar(vtype=GRB.BINARY, lb=0)
            alpha[e][h] = m.addVar(vtype=GRB.BINARY)  # , lb=0, obj=G[e[0]][e[1]]['c'])
            ti[e][h] = m.addVar(vtype=GRB.CONTINUOUS, lb=0)
            for h2 in vehicles:
                ph[e][h][h2] = m.addVar(vtype=GRB.CONTINUOUS)
                z[e][h][h2] = m.addVar(vtype=GRB.BINARY)
    m.update()

    # constraints
    for e in graph.edges():
        # constraint 10 in "the vehicle platooning problem - appendix B"
        # m.addConstr( y[e] == alpha[e][h] + quicksum(((1-saving) * (x[e][h] - alpha[e][h])) for h in vehicles))

        for h in vehicles:

            m.addConstr(y[e][h] == alpha[e][h] + ((1 - saving) * (x[e][h] - alpha[e][h])))

            # constraint 11 in "the vehicle platooning problem"
            m.addConstr(ti[e][h] <= len(vehicles) * quicksum(graph[e[0]][e[1]]['c'] for e in graph.edges()))
            # constraint 20 in "the vehicle platooning problem - appendix B"
            m.addConstr(alpha[e][h] + quicksum(ph[e][h][h2] for h2 in vehicles[0:vehicles.index(h)]) >= x[e][h])

            # constraint 21 in  "the vehicle platooning problem - appendix B"
            m.addConstr(alpha[e][h] <= x[e][h])
            for e2 in graph.edges():
                if [e[0]] == [e2[1]]:
                    # constraint 14 in  "the vehicle platooning problem - appendix B"
                    m.addConstr(ti[e][h] - ti[e2][h] - big_m * (x[e][h] + x[e2][h]) >= graph[e2[0]][e2[1]]['c'] - 2 * big_m)

            for h2 in vehicles:
                if h > h2:
                    # constraint 22 in "the vehicle platooning problem - appendix B"
                    m.addConstr(alpha[e][h] <= 1 - ph[e][h][h2])

                #     # constraint 20 in "the vehicle platooning problem - appendix B"
                # else:
                #     m.addConstr( alpha[e][h] + quicksum( ph[e][h][vehicles[n]] for n in range(0,vehicles.index(h)+1)) >= x[e][h])

                if h != h2:
                    # constraints 15 - 19 in "the vehicle platooning problem - appendix B"
                    m.addConstr(big_m * (1 - ph[e][h][h2]) + (ti[e][h] - ti[e][h2]) >= 0)
                    m.addConstr(big_m * (1 - ph[e][h][h2]) + (ti[e][h2] - ti[e][h]) >= 0)
                    m.addConstr(2 * ph[e][h][h2] - (x[e][h] + x[e][h2]) <= 0)
                    m.addConstr(ph[e][h][h2] >= (x[e][h2] + x[e][h] - 1) + (ti[e][h] - ti[e][h2]) - big_m * z[e][h][h2])
                    m.addConstr(ph[e][h][h2] >= (x[e][h2] + x[e][h] - 1) + (ti[e][h2] - ti[e][h]) - big_m * (1 - z[e][h][h2]))

    # constraint for flow condition of vehicles (constraint 6 in "the vehicle platooning problem - appendix B"
    for v in graph.nodes():
        for h in vehicles:
            if v == s[h]:
                b = 1
            elif v == t[h]:
                b = -1
            else:
                b = 0
            m.addConstr(quicksum(x[e][h] for e in graph.out_edges(v)) - quicksum(x[e][h] for e in graph.in_edges(v)) == b)
    print("optimization modell is complete, optimization prozess can start")
    # m.setObj()
    m.optimize()
    print("----------------")

    # print("status : ", m.getAttr(GRB.Attr.Status))
    # Output
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

    return m.ObjVal, p, eids
