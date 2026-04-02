import collections
import subprocess
from neo4jrestclient.client import GraphDatabase
import pycurl
from StringIO import StringIO
import time
import yaml
import psycopg2
import platform
import numpy as np


def initdb(dbuser, dbpass):


    db = GraphDatabase("http://localhost:7474", username=dbuser, password=dbpass)

    return db

def relabelnodes():
    query = "MATCH (n:vehicle) REMOVE n:vehicle SET n:veh"
    db = initdb()
    db.query(query)


def relabelrelationships():
    query = "MATCH (s)-[r:ends]->(e) " \
            "DELETE r " \
            "CREATE (s)-[:ENDATLOCATION]->(e)"
    db = initdb()
    db.query(query)

def getrandomndoesinregion(db, starta, startc, startd, startb, enda, endc, endd, endb):

    repeat = True

    while repeat:
        try:
            basequery = "MATCH (n:loc) WHERE n.lat > "+ str(startc) +" AND n.lat < " + str(starta) + " AND n.lon > " + str(startd) + " AND n.lon < " + str(startb)
            query = basequery + " WITH count(n) as c WITH  round(rand()*c) as r  return r"
            skip = db.query(query)
            skip = int(skip[0][0])
            query = basequery + "  RETURN id(n) SKIP " + str(skip) + " LIMIT 1"
            startnode = db.query(query)
            startnode = startnode[0][0]


            basequery = "MATCH (n:loc) WHERE n.lat > "+ str(endc) +" AND n.lat < " + str(enda) + " AND n.lon > " + str(endd) + " AND n.lon < " + str(endb)
            query = basequery + " WITH count(n) as c WITH  round(rand()*c) as r  return r"
            skip = db.query(query)
            skip = int(skip[0][0])
            query = basequery + "  RETURN id(n) SKIP " + str(skip) + " LIMIT 1"
            endnode = db.query(query)
            endnode = endnode[0][0]

            query = "call proceduretest.aStarPlugin(" + str(startnode) + ", " + str(endnode) + ", 'distance', 'lat', 'lon', 'coordinates', ['NEIGHBOUR'], [],[], 'both') yield path  WITH  path, extract(n IN nodes(path) | id(n)) as idn, extract(r IN relationships(path) | r.distance) as distance return idn, distance"
            path = db.query(query)

            weights = path.elements[0][1]
            distance = np.sum(weights)

            print "..."
            print distance
            print "+++"

            repeat = False
            if distance is None:
                repeat = True
                print "repeat"
        except:
            repeat = True
            print "path not exists or skip is to large"

    return startnode, endnode


def createvehicle(db, start, end):
    print start
    print end
    query = "MATCH (s:loc),(e:loc) " \
            "WHERE id(s) = " + str(start) + " AND id(e) = " + str(end) + " " \
            "CREATE (s)<-[r1:STARTATLOCATION]-(v:veh)-[r2:ENDATLOCATION]->(e) RETURN r1,r2"
    print query

    db.query(query)

dbuser = "neo4j"
dbpass = "12345678"

# ---a---
# |     |
# d     b lat
# |__c__|
#   lon

db = initdb(dbuser, dbpass)

for x in range(0, 30):
    start, end = getrandomndoesinregion(db, 48.442, 47.549, 6, 15, 55, 52.862, 6, 15)
    createvehicle(db, start, end)

    #start, end = getrandomndoesinregion(db, 51.292, 50.832, 6, 15, 55, 53.383, 6, 15)
    #createvehicle(db, start, end)

    #start, end = getrandomndoesinregion(db, 48.442, 47.549, 6, 15, 51.292, 50.832, 6, 15)
    #createvehicle(db, start, end)


#print(str(start) +" "+ str(end))