import networkx as nx
from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time
import lppl
import difflib
import platform
import psycopg2


# Connection to database
#db = GraphDatabase("http://localhost:7474", username="neo4j", password="preprocessing")

#db = GraphDatabase("http://localhost:7474", username="neo4j", password="x")
db = GraphDatabase("http://localhost:7474", username="neo4j", password="12345678")

# Load road network from database
query = "MATCH p=(n1)-[r:NEIGHBOUR]->(n2) RETURN id(n1),id(n2),r.distance, id(r)"
results = db.query(query)

cedges = len(results)

# Create networkx graph
G = nx.DiGraph()
for r in results:
    G.add_edge(r[0],r[1], {'c': r[2], 'id': r[3]})
    G.add_edge(r[1],r[0], {'c': r[2], 'id': r[3]})

limit = 10
if len(sys.argv) > 1:
    limit = sys.argv[1]
testid = -1
if len(sys.argv) > 2:
    testid = sys.argv[2]

if(int(testid) > -1):
    log = True;
else:
    log = False;


# Get vehicles from database
query ="MATCH p=(s:loc)<-[r1:STARTATLOCATION]-(n:veh)-[r2:ENDATLOCATION]->(e:loc) " \
       "RETURN id(s),id(n),id(e) LIMIT "+ str(limit)
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
(val, p, eids) = lppl.lp(vehicles, G, s ,t, 0.1)
time_elapsed = (time.clock() - time_start)


# Results output of lp computation
for h in vehicles:
    #print p[h]
    print h,eids[h]



m = [[0 for x in range(len(vehicles))] for y in range(len(vehicles))]

#md = {}

for i in range(0, len(vehicles)):
    v1 = vehicles.keys()[i]
    #md[vehicles[v1]] = {}
    for d in range(i+1, len(vehicles)):
        v2 = vehicles.keys()[d]

        sm = difflib.SequenceMatcher(None, eids[v1], eids[v2])
        #md[vehicles[v1]][vehicles[v2]] = sm.ratio()

        #if sm.ratio() > 0:
            #print vehicles[v1], "(",i,")", vehicles[v2],"(",d,")", "->", sm.ratio()
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

print platform.processor()
print platform.platform()
print platform.system()
print platform.version()

cedges = db.query("MATCH ()-[r:NEIGHBOUR]->() RETURN count(r)")


sql = " BEGIN; INSERT INTO optimum (objectiveValue, lpt, testid) VALUES ('" + str(val) + "', '" + str(time_elapsed) + "', '" + str(testid) + "'); COMMIT;"


if log:
    try:
        connection = psycopg2.connect("dbname='platoon' user='admin' host='139.174.101.155' port=5432 password='admin123'")
        #connection = psycopg2.connect("dbname='platoon' user='pascal' host='139.174.101.155' port=5432 password='zfrZVFX4'")
        with connection.cursor() as cursor:
            res = cursor.execute(sql)
            print(sql)
    except:
        print "I am unable to connect to the database"
    finally:
        connection.close()
