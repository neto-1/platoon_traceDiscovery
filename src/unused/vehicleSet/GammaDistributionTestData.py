from neo4jrestclient.client import GraphDatabase
import numpy as np
import random
import math
import DBOperations

class GammaDistribution(object):
    def __init__(self,db,longestPath,scaleValue):
        self.db=db
        self.longestPath=longestPath
        self.scaleValue=scaleValue
        self.scaledLongestPath=0


    # Define the ranges of lengths, in which the vehicles are generated
    def DefineDistributionRanges(self,numOfVehicles):
        finalRange=[]
        # Gamma distribution uses the mean and standard deviation of the normal distribution
        # and compute the shape and scale parameters of gamma distribution
        # Let mu and sd be the parameters of X on the original scale. The shape parameter (alpha) and scale parameter (theta) can be found as:
        # alpha = mu^2 / sd^2
        # theta = sd^2 / mu
        mu,sigma=DBOperations.GetNormalDistributionsParameters(self.longestPath,self.scaleValue)
        alpha= math.pow(mu,2) / math.pow(sigma,2)
        theta= math.pow(sigma,2) / mu
        mainRange = np.random.gamma(alpha, theta, numOfVehicles)
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
                    print finalRanges
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
        DBOperations.RunQueries(self.db,startNodesId,endNodesId,distances,paths_nodes,numOfVehicles,"gamma")
#
# dbuser = "neo4j"
# dbpass = "12345678"
# db = GraphDatabase("http://localhost:7474", username=dbuser, password=dbpass)
#
# x=GammaDistribution(db,100.5,0.5) # (database connection, the length of longest path, the scale value [0,1])
# x.CreateVehicle(10)   # (number of vehicles)
