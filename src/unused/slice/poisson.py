import numpy as np
from neo4jrestclient.client import GraphDatabase

# config
dbuser = "neo4j"
dbpass = "12345678"


db = GraphDatabase("http://localhost:7474", username=dbuser, password=dbpass)



def getvehicles(skip, limit):
        query = "MATCH (s)<-[r1:STARTATLOCATION]-(v:veh)-[r2:ENDATLOCATION]->(e) " \
                "RETURN id(v) as v,id(s) as s,id(e) as e SKIP "+ str(skip) +" LIMIT "+ str(limit) +""
        vehicles = db.query(query)
        return vehicles

def deleteallvehicles():
        query = "MATCH (n:veh) DETACH DELETE n"
        db.query(query)


def equallyslice(path, parts):

        # 0 -> 1 -->
        # 1 -> 2 --]-->
        # 2 -> 3 --]--]-->
        # 3 -> 4 --]--]--]-->

        nodes = path.elements[0][0]
        weights = path.elements[0][1]

        distance = np.sum(weights)
        # print "----"
        # print distance
        rangepart = distance / parts
        # print rangepart
        # print parts
        # print "---------"
        rng = rangepart
        weightsum = 0

        slicenodes = []
        weightsum = 0
        sliced = 0

        start = nodes[0]
        slicenodes.append(nodes[0])
        for i in range(len(weights)):
                weightsum += weights[i]

                #print weightsum
                if weightsum >= rng:
                        if (distance - weightsum) < (rangepart / 2) :
                                #print "break"
                                break
                        # print "* " + str(rng) + " *"
                        # print "> " + str(weightsum) + " <"
                        slicenodes.append(nodes[i])
                        rng = rng + rangepart
        slicenodes.append(nodes[-1])
        return slicenodes

def poissonpartitioning(path, ev):
        nodes = path.elements[0][0]
        weights = path.elements[0][1]
        distance = np.sum(weights)

        breakdistance = 700


        nu = distance / ev

        slices = np.random.poisson(nu, 1)[0]
        slicedistance = distance / (slices + 1)#
        parts = slices + 1

        return parts


def createvehicles(slicenodes):
        for i in range(len(slicenodes)):
                if (i+1) < len(slicenodes):
                        query = "MATCH (s:loc),(e:loc) " \
                                "WHERE id(s) = " + str(slicenodes[i]) + " AND id(e) = " + str(slicenodes[i+1]) + " " \
                                                                                       "CREATE (s)<-[r1:STARTATLOCATION]-(v:vehicle)-[r2:ENDATLOCATION]->(e) " \
                                                                                       "RETURN r1,r2"
                        db.query(query)


#deleteallvehicles()

vehicles = getvehicles(0,30)
ev = 600


for vehicle in vehicles.elements:
        query = "call proceduretest.aStarPlugin(" + str(vehicle[1]) + ", " + str(vehicle[2]) + ", 'distance', 'lat', 'lon', 'coordinates', ['NEIGHBOUR'], [],[], 'both') yield path  WITH  path, extract(n IN nodes(path) | id(n)) as idn, extract(r IN relationships(path) | r.distance) as distance return idn, distance"
        # shortest path of current vehicle
        print query
        print str(vehicle[1]) + ", " + str(vehicle[2])
        path = db.query(query)



        # determine number of partitions with random poisson distribution
        parts = poissonpartitioning(path, ev)

        # slice normally
        slicenodes = equallyslice(path, parts)

        # insert sliced vehicles into database
        #createvehicles(slicenodes)
