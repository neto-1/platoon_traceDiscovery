import numpy as np
import random
import DBOperations
from neo4jrestclient.client import GraphDatabase

class PoissonDistribution(object):
    def __init__(self,db,longestPath,scaleValue):
        self.db=db
        self.longestPath=longestPath
        self.scaleValue=scaleValue
        self.scaledLongestPath=0

    # Define the ranges of lengths, in which the vehicles are generated
    def DefineDistributionRanges(self,numOfVehicles):
        finalRange=[]
        # Poisson distribution uses the lambda and sigma
        mu,sigma=DBOperations.GetNormalDistributionsParameters(self.longestPath,self.scaleValue)
        lam=mu
        mainRange = np.random.poisson(lam, numOfVehicles)
        for val in mainRange:
            tempRange=[]
            tempRange.append(val-0.9)
            tempRange.append(val+0.9)
            finalRange.append(tempRange)
        return finalRange

    def create_vehicle(self,numOfVehicles):
        finalRanges=self.DefineDistributionRanges(numOfVehicles)
        query = "match (n:loc) return ID(n)"
        result = self.db.query(query)
        startNodesId=[]
        endNodesId=[]
        distances=[]
        paths_nodes=[]
        count=0
        while count != numOfVehicles:
            rand1= random.randrange(0,len(result)-1)
            rand2= random.randrange(0,len(result)-1)
            node1 = result[rand1][0]
            node2 = result[rand2][0]
            query2 = "call proceduretest.aStarPlugin("+str(node1)+", "+str(node2)+", 'distance', 'lat', 'lon', 'coordinates', ['NEIGHBOUR'], [], [], 'both') yield path  WITH  path, extract(n IN relationships(path) | id(n)) as idn, extract(r IN relationships(path) | r.distance) as distance, extract(m IN nodes(path) | id(m)) as idm return idn, distance, idm"
            path = self.db.query(query2)
            weights = path.elements[0][1]
            distance = np.sum(weights)
            found=False
            for range in finalRanges:
                if distance>=range[0] and distance<=range[1]:
                    finalRanges.remove(range)
                    found=True
                    break
            if found:
                print len(finalRanges),node1,node2,distance
                startNodesId.append(node1)
                endNodesId.append(node2)
                distances.append(round(distance,3))
                paths_nodes.append(path[0][2])
                count=count+1
        DBOperations.RunQueries(self.db,startNodesId,endNodesId,distances,paths_nodes,numOfVehicles,"poisson")

# maxLength =100.5# the maximal length path
# scaleLength = 0.8
# dbuser = "neo4j" # is also already in experiments.py
# dbpass = "12345678" # is also already in experiments.py
# db = GraphDatabase("http://localhost:7474", username=dbuser, password=dbpass) # is also already in experiments.py
# p=PoissonDistribution(db,maxLength,scaleLength)
# p.CreateVehicle(20)
