from neo4jrestclient.client import GraphDatabase
import numpy as np
import random
import DBOperations

class RegionsData(object):
    def __init__(self,db,a,b,c,d): # a,b,c,d latitude coordinates
        self.db=db
        self.a=a
        self.b=b
        self.c=c
        self.d=d

    def GetRegions(self):
        southRegion=[]
        northRegion=[]
        middleRegion=[]
        query="MATCH (n:loc) WHERE n.lat >= "+str(self.a)+" RETURN ID(n)"
        northRegion = self.db.query(query)
        query="MATCH (n:loc) WHERE n.lat <= "+str(self.d)+" RETURN ID(n)"
        southRegion = self.db.query(query)
        query="MATCH (n:loc) WHERE n.lat <= "+str(self.b)+" and n.lat >= "+str(self.c)+" RETURN ID(n)"
        middleRegion = self.db.query(query)
        return northRegion,middleRegion,southRegion

    def create_vehicle(self,numOfVehicles):
        northRegion,middleRegion,southRegion=self.GetRegions()

        longVehicles=int(numOfVehicles/2)
        shortVehicles=numOfVehicles-longVehicles

        longVehiclesNS=int(longVehicles/2)
        longVehiclesSN=longVehicles-longVehiclesNS

        shortVehiclesNM=shortVehiclesMS=shortVehiclesSM=int(shortVehicles/4)
        shortVehiclesMN=shortVehicles-(shortVehiclesNM+shortVehiclesMS+shortVehiclesSM)

        startNodesId=[]
        endNodesId=[]
        distances=[]
        paths_nodes=[]
        count=0
        while count != longVehiclesNS:
            rand1= random.randrange(0,len(northRegion)-1)
            rand2= random.randrange(0,len(southRegion)-1)
            node1 = northRegion[rand1][0]
            node2 = southRegion[rand2][0]
            query2 = "call proceduretest.aStarPlugin("+str(node1)+", "+str(node2)+", 'distance', 'lat', 'lon', 'coordinates', ['NEIGHBOUR'], [], [], 'both') yield path  WITH  path, extract(n IN relationships(path) | id(n)) as idn, extract(r IN relationships(path) | r.distance) as distance, extract(m IN nodes(path) | id(m)) as idm return idn, distance, idm"
            path = self.db.query(query2)
            weights = path.elements[0][1]
            distance = np.sum(weights)
            print count,node1,node2,distance
            startNodesId.append(node1)
            endNodesId.append(node2)
            distances.append(round(distance,3))
            paths_nodes.append(path[0][2])
            count=count+1

        count=0
        while count != longVehiclesSN:
            rand1= random.randrange(0,len(southRegion)-1)
            rand2= random.randrange(0,len(northRegion)-1)
            node1 = southRegion[rand1][0]
            node2 = northRegion[rand2][0]
            query2 = "call proceduretest.aStarPlugin("+str(node1)+", "+str(node2)+", 'distance', 'lat', 'lon', 'coordinates', ['NEIGHBOUR'], [], [], 'both') yield path  WITH  path, extract(n IN relationships(path) | id(n)) as idn, extract(r IN relationships(path) | r.distance) as distance, extract(m IN nodes(path) | id(m)) as idm return idn, distance, idm"
            path = self.db.query(query2)
            weights = path.elements[0][1]
            distance = np.sum(weights)
            print count,node1,node2,distance
            startNodesId.append(node1)
            endNodesId.append(node2)
            distances.append(round(distance,3))
            paths_nodes.append(path[0][2])
            count=count+1

        count=0
        while count != shortVehiclesNM:
            rand1= random.randrange(0,len(northRegion)-1)
            rand2= random.randrange(0,len(middleRegion)-1)
            node1 = northRegion[rand1][0]
            node2 = middleRegion[rand2][0]
            query2 = "call proceduretest.aStarPlugin("+str(node1)+", "+str(node2)+", 'distance', 'lat', 'lon', 'coordinates', ['NEIGHBOUR'], [], [], 'both') yield path  WITH  path, extract(n IN relationships(path) | id(n)) as idn, extract(r IN relationships(path) | r.distance) as distance, extract(m IN nodes(path) | id(m)) as idm return idn, distance, idm"
            path = self.db.query(query2)
            weights = path.elements[0][1]
            distance = np.sum(weights)
            print count,node1,node2,distance
            startNodesId.append(node1)
            endNodesId.append(node2)
            distances.append(round(distance,3))
            paths_nodes.append(path[0][2])
            count=count+1

        count=0
        while count != shortVehiclesMN:
            rand1= random.randrange(0,len(middleRegion)-1)
            rand2= random.randrange(0,len(northRegion)-1)
            node1 = middleRegion[rand1][0]
            node2 = northRegion[rand2][0]
            query2 = "call proceduretest.aStarPlugin("+str(node1)+", "+str(node2)+", 'distance', 'lat', 'lon', 'coordinates', ['NEIGHBOUR'], [], [], 'both') yield path  WITH  path, extract(n IN relationships(path) | id(n)) as idn, extract(r IN relationships(path) | r.distance) as distance, extract(m IN nodes(path) | id(m)) as idm return idn, distance, idm"
            path = self.db.query(query2)
            weights = path.elements[0][1]
            distance = np.sum(weights)
            print count,node1,node2,distance
            startNodesId.append(node1)
            endNodesId.append(node2)
            distances.append(round(distance,3))
            paths_nodes.append(path[0][2])
            count=count+1

        count=0
        while count != shortVehiclesMS:
            rand1= random.randrange(0,len(middleRegion)-1)
            rand2= random.randrange(0,len(southRegion)-1)
            node1 = middleRegion[rand1][0]
            node2 = southRegion[rand2][0]
            query2 = "call proceduretest.aStarPlugin("+str(node1)+", "+str(node2)+", 'distance', 'lat', 'lon', 'coordinates', ['NEIGHBOUR'], [], [], 'both') yield path  WITH  path, extract(n IN relationships(path) | id(n)) as idn, extract(r IN relationships(path) | r.distance) as distance, extract(m IN nodes(path) | id(m)) as idm return idn, distance, idm"
            path = self.db.query(query2)
            weights = path.elements[0][1]
            distance = np.sum(weights)
            print count,node1,node2,distance
            startNodesId.append(node1)
            endNodesId.append(node2)
            distances.append(round(distance,3))
            paths_nodes.append(path[0][2])
            count=count+1

        count=0
        while count != shortVehiclesSM:
            rand1= random.randrange(0,len(southRegion)-1)
            rand2= random.randrange(0,len(middleRegion)-1)
            node1 = southRegion[rand1][0]
            node2 = middleRegion[rand2][0]
            query2 = "call proceduretest.aStarPlugin("+str(node1)+", "+str(node2)+", 'distance', 'lat', 'lon', 'coordinates', ['NEIGHBOUR'], [], [], 'both') yield path  WITH  path, extract(n IN relationships(path) | id(n)) as idn, extract(r IN relationships(path) | r.distance) as distance, extract(m IN nodes(path) | id(m)) as idm return idn, distance, idm"
            path = self.db.query(query2)
            weights = path.elements[0][1]
            distance = np.sum(weights)
            print count,node1,node2,distance
            startNodesId.append(node1)
            endNodesId.append(node2)
            distances.append(round(distance,3))
            paths_nodes.append(path[0][2])
            count=count+1
        print len(startNodesId)
        DBOperations.RunQueries(self.db,startNodesId,endNodesId,distances,paths_nodes,numOfVehicles,"region")

#
# dbuser = "neo4j"
# dbpass = "12345678"
# db = GraphDatabase("http://localhost:7474", username=dbuser, password=dbpass)
# # #
# x=RegionsData(db,49.53,49.38,49.35,49.24) # (database connection, north region, up middle region, down middle region, south region)
# x.CreateVehicle(10)
