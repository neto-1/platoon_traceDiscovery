import networkx as nx
from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time
import ilppl
import difflib



vehicles = {1:1, 2:2}

s = {} #Startknoten
t = {} #Zielknoten
s[1] = 1
t[1] = 2
s[2] = 3
t[2] = 4
G = nx.DiGraph()
G.add_edges_from([(1,2, {'c': 2.99, 'id': 1}),(1,5, {'c': 1, 'id': 3}),(3,4, {'c': 2.99, 'id': 2}),
                  (3,5, {'c': 1, 'id': 4}),(5,6, {'c': 1, 'id': 7}),(6,2, {'c': 1, 'id': 5}),(6,4, {'c': 1, 'id': 6})])




# Time measurement of LP execution
time_start = time.clock()
# Run LP
(val, p, eids) = ilppl.lp(vehicles, G, s ,t)
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
print "vehicles", i
print "value", val
#print m
#print md