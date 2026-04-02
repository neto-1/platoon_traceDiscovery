import networkx as nx
from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time
import lpplTime
import fg
#import pymysql.cursors
import psycopg2
import platform

time_init = time.clock()
# init database
db = GraphDatabase("http://localhost:7474", username="neo4j", password="12345678")

query = "MATCH (g:Group)-[r:INGROUP]->(v:Vehicle),(e:loc)-[:END]-(v)-[:START]-(s:loc)" \
        "RETURN DISTINCT id(v), id(e), id(s)"

results = db.query(query)

vehicles = []
s = {}
t = {}
for r in results:
    vehicles.append(r[0])
    s[r[0]] = r[2]
    t[r[0]] = r[1]

query = "MATCH (g:Group)-[r:INGROUP]->(v:Vehicle) RETURN id(g), id(v)"
results = db.query(query)

groups = {}
for r in results:
    groupId = r[0]
    vehicleId = r[1]
    if groupId not in groups:
        groups[groupId] = []
    groups[groupId].append(vehicleId)

time_init = time.clock() - time_init
time_start = time.clock()
p = {}
groupInfo = {}
ing = 0
outg = 0

if len(groups) > 0:
    for key, group in groups.items():
        print(key)
        query = "MATCH (g:Group)-[r:UNION]->(p:Polygon) WHERE id(g) = " + str(key) + " RETURN p.Poly"
        results = db.query(query)
        query = "WITH 'POLYGON(("
        for r in results:
            for i in range(0, len(r[0])):
                query = query + " " + str(r[0][i])
                if (i % 2 != 0) & (i < (len(r[0]) - 1)):
                    query = query + ", "
        # query = query + "))' as polygon CALL spatial.intersects('geometry',polygon) YIELD node as n1 with n1 MATCH (n1)-[r:neighbourEdges]->(n2) RETURN id(n1), id(n2), r.distance, id(r)"
        query = query + "))' as polygon CALL spatial.intersects('geom',polygon) YIELD node as n1 with n1 MATCH (n1)-[r:NEIGHBOUR]->(n2) RETURN id(n1), id(n2), r.distance, id(r)"
        print(query)
        results = db.query(query)
        G = nx.DiGraph()
        for r in results:
            G.add_edge(r[0], r[1], c=r[2], id=r[3])
            G.add_edge(r[1], r[0], c=r[2], id=r[3])
        print("group ", key, group)
        time_solve_this_group = time.clock()
        (val, paths, eids) = lpplTime.lp(group, G, s, t, 0.1)



        shortestPathValue = 0
        query = "MATCH (g:Group)-[r:INGROUP]->(v:Vehicle) WHERE id(g)= " + str(key) + "  RETURN sum(v.shortestpath_cost) as sp"
        results = db.query(query)
        for r in results:
            shortestPathValue = r[0]

        p[key] = shortestPathValue - val
        saving = (p[key]*100/shortestPathValue)

        print("saving group " + str(key) + ":", p[key], " SP: " + str(shortestPathValue) + " PSP: " + str(val) + " saving: " + str(saving))
        groupInfo[key] = [p[key], shortestPathValue, val, (p[key]*100/shortestPathValue)]
        if saving > 0:
            ing = ing + 1
        else:
            outg = outg + 1

(model, groups, g) = fg.lp(vehicles, groups, p)

time_elapsed = (time.clock() - time_start)

sumSP = 0
sumPSP = 0
usedVehicles = []

for (key, group) in groups.items():
    if g[key].X > 0.99:

        print("-----")
        if key == groups.keys()[-1]:
            print("last")
        print(str(key) + " " + str(groups.keys()[-1]))

        usedVehicles.extend(group)
        sumSP += groupInfo[key][1]
        sumPSP += groupInfo[key][2]


print("time")
print(time_elapsed)

print ("Objective value")
print(model.ObjVal)

print("groupInfo")
print(groupInfo)

print("SP")
print(sumSP)
print(sumPSP)


