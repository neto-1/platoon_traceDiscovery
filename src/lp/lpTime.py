from gurobipy import *
import networkx as nx
import time


def lp_time(vehicles, graph, s, t, saving):
    # LP
    m = Model("Time")
    m.setParam("OutputFlag", False)

    # initiate the different variables
    # direct decision variables
    x = {}  # vehicle uses an edge
    y = {}  # timestamp cost of an edge (for every time a vehicle traverses the edge we have to buy it)
    times = {}  # the time a vehicle starts to use an edge

    # indirect decision variables
    platoon = {}  # two vehicles drive over the same edge in the same time
    helper = {}  # helping binary variable for constraint 18 and 19

    # creating the "big number" B for the time constraints
    big_m = 2 * len(vehicles) * quicksum(graph[e[0]][e[1]]['c'] for e in graph.edges())

    # start_creating_constraints = time.clock()
    # !!!!!! initiate the variable lists !!!!!!
    for e in graph.edges():
        y[e] = {}
        x[e] = {}
        times[e] = {}
        platoon[e] = {}
        helper[e] = {}

        for h in vehicles:

            x[e][h] = m.addVar(vtype=GRB.BINARY, lb=0, ub=1, obj=(1-saving) * graph[e[0]][e[1]]['c'], name="edge " + str(e) + " " + str(h))
            y[e][h] = m.addVar(vtype=GRB.BINARY, lb=0, ub=1, obj=saving * graph[e[0]][e[1]]['c'], name="timestamp " + str(e) + " " + str(h))
            times[e][h] = m.addVar(vtype=GRB.INTEGER, lb=0, obj=0, name="times " + str(e) + " " + str(h))
            platoon[e][h] = {}
            helper[e][h] = {}

            for g in vehicles:
                if g <= h:
                    platoon[e][h][g] = m.addVar(vtype=GRB.BINARY, lb=0, ub=1, obj=0, name="platoon " + str(e) + str(h) + " " + str(h))
                    helper[e][h][g] = m.addVar(vtype=GRB.BINARY, lb=0, ub=1, obj=0, name="helper" + str(e) + str(h) + " " + str(h))
    m.update()

    # !!!!!! constraints of the model !!!!!!
    # constraint related to nodes
    for v in graph.nodes():

        # constraint for flow condition of vehicles
        for h in vehicles:
            if v == s[h]:
                b = 1
            elif v == t[h]:
                b = -1
            else:
                b = 0
            m.addConstr(lhs=quicksum(x[e][h] for e in graph.out_edges(v)) - quicksum(x[e][h] for e in graph.in_edges(v)), sense=GRB.EQUAL, rhs=b, name="path C" +str(v) + " " + str(h))

            # the constraint for the time variable
            for edge_in in graph.in_edges(v):
                for edge_out in graph.out_edges(v):
                    m.addConstr(lhs=times[edge_out][h] - times[edge_in][h] - big_m * (x[edge_in][h] + x[edge_out][h]), rhs=graph[edge_in[0]][edge_in[1]]['c'] - 2 * big_m, sense=GRB.GREATER_EQUAL, name="pathtime C" + str(edge_in) + str(edge_out))

    # constraints related to edges
    for h in vehicles:
        for e in graph.edges():
            # restrict the maximal time
            m.addConstr(lhs=times[e][h], sense=GRB.LESS_EQUAL, rhs=len(vehicles) * quicksum(graph[e[0]][e[1]]['c'] for e in graph.edges()), name="maxTime C" + str(e) + str(h))

            # constraint to enable the timestamp costs
            m.addConstr(lhs=y[e][h] + quicksum(platoon[e][h][g] for g in vehicles if g < h), sense=GRB.GREATER_EQUAL, rhs=x[e][h], name="timestamp C1" + str(e) + str(h))
            m.addConstr(lhs=y[e][h], sense=GRB.LESS_EQUAL, rhs=x[e][h], name="timestamp C2" + str(e) + str(h))

            for g in vehicles:
                if g <= h:

                    # the 5 constraints to enable the platoon variable: 1 if two vehicle travel over the same edge at the same time, 0 otherwise
                    m.addConstr(lhs=big_m * (1 - platoon[e][h][g]) + (times[e][h] - times[e][g]), sense=GRB.GREATER_EQUAL, rhs=0, name="platoon C1 " + str(e) + str(h) + " " + str(g))
                    m.addConstr(lhs=big_m * (1 - platoon[e][h][g]) + (times[e][g] - times[e][h]), sense=GRB.GREATER_EQUAL, rhs=0, name="platoon C2 " + str(e) + str(h) + " " + str(g))
                    m.addConstr(lhs=2 * platoon[e][h][g] - x[e][h] - x[e][g], sense=GRB.LESS_EQUAL, rhs=0, name="platoon C3 " + str(e) + str(h) + " " + str(g))
                    m.addConstr(lhs=platoon[e][h][g], sense=GRB.GREATER_EQUAL, rhs=x[e][h] + x[e][g] + (times[e][h] - times[e][g]) - big_m * helper[e][h][g] - 1, name="platoon C4 " + str(e) + str(h) + " " + str(g))
                    m.addConstr(lhs=platoon[e][h][g], sense=GRB.GREATER_EQUAL, rhs=x[e][h] + x[e][g] + (times[e][g] - times[e][h]) - big_m * (1 - helper[e][h][g]) - 1, name="platoon C5 " + str(e) + str(h) + " " + str(g))

                    # constraint to enable the timestamp costs
                    if g != h:
                        m.addConstr(lhs=y[e][h], sense=GRB.LESS_EQUAL, rhs= 1 - platoon[e][h][g], name="timestamp C3" + str(e) + str(h))
    # for h in vehicles:
    #    m.addConstr(lhs=x[(41, 51)][h], sense=GRB.EQUAL, rhs=1)
    # end_creating_constraints = time.clock() - start_creating_constraints
    # print("optimization model is complete after " + str(end_creating_constraints ) + ", optimization process can start")

    # m.setObj()
    m.optimize()

    if m.status == 3:
        m.computeIIS()
        print("INFEAASIBLEEEE!")
        for c in m.getConstrs():
            if c.IISConstr > 0:
                print(c.ConstrName)
                print(c.IISConstr)

    # print("status : ", m.getAttr(GRB.Attr.Status))
    # Output
    p = {}
    eids = {}

    for h in vehicles:
        succ = {}
        succedges = []

        for e in graph.edges():

            if x[e][h].X > 0.99:

                #print("time " + str(times[e][h].X) + " at " + str(e[0]) + " of edge " + str(e))
                #print("timestamp of " + str(h) + " : " + str(y[e][h].X))
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
