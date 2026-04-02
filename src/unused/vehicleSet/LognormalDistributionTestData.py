from neo4jrestclient.client import GraphDatabase
import numpy as np
import random
import math
import DBOperations

class LognormalDistribution(object):
    def __init__(self,db,longestPath,scaleValue):
        self.db=db
        self.longestPath=longestPath
        self.scaleValue=scaleValue
        self.scaledLongestPath=0

    # Define the ranges of lengths, in which the vehicles are generated
    def DefineDistributionRanges(self,numOfVehicles):
        finalRange=[]
        # Lognormal distribution uses the mu and sigma of the underlying normal distribution
        # and compute the new logarithmic mu and sigma
        # Let m and s be the mu and sd of X on the original scale. The appropriate mu and sd on the log scale can be found as:
        # mu(log(X))= log(m) - 1/2 * log[(s/m)^2 +1]
        # sd(log(X))= math.sqrt(log[(s/m)^2+1])
        mu,sigma=DBOperations.GetNormalDistributionsParameters(self.longestPath,self.scaleValue)
        log_mu= math.log(mu) - 0.5* math.log(math.pow(sigma/mu,2)+1)
        log_sigma= math.sqrt(math.log(math.pow(sigma/mu,2)+1))
        mainRange = np.random.lognormal(log_mu, log_sigma, numOfVehicles)
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
                    # print finalRanges
                    finalRanges.remove(range)
                    found=True
                    break
            if found:
                # print len(finalRanges),node1,node2,distance
                startNodesId.append(node1)
                endNodesId.append(node2)
                distances.append(round(distance,3))
                paths_nodes.append(path[0][2])
                count=count+1
        DBOperations.RunQueries(self.db,startNodesId,endNodesId,distances,paths_nodes,numOfVehicles,"lognormal")

# dbuser = "neo4j"
# dbpass = "12345678"
# db = GraphDatabase("http://localhost:7474", username=dbuser, password=dbpass)
#
# x=LognormalDistribution(db,100.5,0.5) # (database connection, the length of longest path, the scale value [0,1])
# x.CreateVehicle(10)   # (number of vehicles)
