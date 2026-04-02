import networkx as nx
from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time
import lppl

db = GraphDatabase("http://localhost:7474", username="neo4j", password="12345678")
key = 4513



query = "MATCH (g:Group) WHERE id(g) = "+ str(key) +" RETURN g.Poly"
results = db.query(query)
query = "WITH 'POLYGON(("
for r in results:
    for i in range(0, len(r[0])):
        query = query + " " + str(r[0][i])
        if ((i % 2 != 0) &  (i < (len(r[0])-1)) ):
            query = query + ", "
query = query + "))' as polygon CALL spatial.intersects('geom',polygon) YIELD node as n1 with n1 MATCH (n1)-[r:NEIGHBOUR]->(n2) RETURN id(n1), id(n2), r.distance, id(r)"

print(query)

results = db.query(query)
for r in results:
    print(r)