import networkx as nx
from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time


# init database
db = GraphDatabase("http://localhost:7474", username="neo4j", password="x")
query = "MATCH (g:Group)-[r:vehgroup]->(v:veh) RETURN DISTINCT id(v)"
results = db.query(query)


for r in results:
    print(r[0])


vehicles = {1:1, 2:2, 3:3, 4:4}
groups = {1:[1,2],2:[2,3],3:[3,4]}

# Einsparung der jeweiligen Gruppe ( Summe SP aller Fahrzeuge - LP Wert)
p = {1:10, 2:3, 3:3}

model = Model("Grouping")
model.setParam("OutputFlag", True)
model.ModelSense = GRB.MAXIMIZE


g = {}

# Variablen und Zielfunktion
# foreach mit key und group-liste
for (i, group) in groups.items():
    print(i, p)
    print(p[i])
    g[i] = model.addVar(vtype=GRB.BINARY, obj=p[i])

# Update
model.update()

# Nebenbedingungen
for h in vehicles:
    model.addConstr(quicksum(g[i] for (i, group) in groups.items() if h in group ) <= 1)

model.optimize()


