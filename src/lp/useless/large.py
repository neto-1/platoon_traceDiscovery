import networkx as nx
from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time
import lppl
import difflib



# Connection to database
db = GraphDatabase("http://localhost:7474", username="neo4j", password="preprocessing")

# Load road network from database
query = "MATCH p=(n1)-[r:NEIGHBOUR]->(n2) RETURN id(n1),id(n2),r.distance, id(r)"
results = db.query(query)

# Create networkx graph
G = nx.DiGraph()
for r in results:
    G.add_edge(r[0],r[1], {'c': r[2], 'id': r[3]})
    G.add_edge(r[1],r[0], {'c': r[2], 'id': r[3]})

limit = 2
# Get vehicles from database
query ="MATCH p=(s:loc)<-[r1:STARTATLOCATION]-(n:veh)-[r2:ENDATLOCATION]->(e:loc), " \
       "sp = shortestPath((s)-[:NEIGHBOUR *..150]-(e)) where length(sp) > 1 RETURN id(s),id(n),id(e),length(sp) LIMIT "+ str(limit)

query = "MATCH p=(s:loc)<-[r1:STARTATLOCATION]-(n:veh)-[r2:ENDATLOCATION]->(e:loc)RETURN id(s),id(n),id(e)LIMIT "+ str(limit)

results = db.query(query)

print query


# Convert vehicles to special format
s = {} #Startknoten
t = {} #Zielknoten
vehicles = {}
i = 0
for r in results:
    s[i] = r[0]
    t[i] = r[2]
    vehicles[i] = r[1]
    i = i + 1




 # List
# vehicles = {1:1, 2:2}
#
# s = {} #Startknoten
# t = {} #Zielknoten
# s[1] = 1
# t[1] = 2
# s[2] = 3
# t[2] = 4
# G = nx.DiGraph()
# G.add_edges_from([(1,2, {'c': 2.99, 'id': 1}),(1,5, {'c': 1, 'id': 3}),(3,4, {'c': 2.99, 'id': 2}),
#                   (3,5, {'c': 1, 'id': 4}),(5,6, {'c': 1, 'id': 7}),(6,2, {'c': 1, 'id': 5}),(6,4, {'c': 1, 'id': 6})])
#



# Time measurement of LP execution
time_start = time.clock()
# Run LP
(val, p, eids) = lppl.lp(vehicles, G, s ,t)
time_elapsed = (time.clock() - time_start)


# Results output of lp computation
for h in vehicles:
    #print p[h]
    print h,eids[h]



m = [[0 for x in range(len(vehicles))] for y in range(len(vehicles))]

#md = {}

for i in range(0, len(vehicles)):
    print "---"
    v1 = vehicles.keys()[i]
    #md[vehicles[v1]] = {}

    for d in range(i+1, len(vehicles)):


        v2 = vehicles.keys()[d]




        sm = difflib.SequenceMatcher(None, eids[v1], eids[v2])
        #md[vehicles[v1]][vehicles[v2]] = sm.ratio()

        if sm.ratio() > 0:
            print vehicles[v1], "(",i,")", vehicles[v2],"(",d,")", "->", sm.ratio()



        m[i][d] = sm.ratio()
        #sm = difflib.SequenceMatcher(None, eids.values()[i], eids.values()[d])
        #print str(vehicles.values()[i]), " ", str(vehicles.values()[d]), " -> ", sm.ratio()
        #print sm.ratio()



# s1 = [1,2,3,4,5]
# s2 = [3]
# sm = difflib.SequenceMatcher(None, s1, s2)
# print sm.ratio()
# print sm.get_matching_blocks()

print "time", time_elapsed
print "vehicles", i+1
print "value", val
#print m
#print md