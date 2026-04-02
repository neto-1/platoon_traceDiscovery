from gurobipy import *
import networkx as nx


def lp(vehicles, groups, p):
    model = Model("Grouping")
    model.setParam("OutputFlag", False)
    model.ModelSense = GRB.MAXIMIZE

    g = {}
    # Variablen und Zielfunktion
    # foreach mit key und group-liste
    for (i, group) in groups.items():
        g[i] = model.addVar(vtype=GRB.BINARY, obj=p[i])
    # Update
    model.update()

    # Nebenbedingungen
    for h in vehicles:
        model.addConstr(quicksum(g[i] for (i, group) in groups.items() if h in group) <= 1)

    model.optimize()

    return model, groups, g
