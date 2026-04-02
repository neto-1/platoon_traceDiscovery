'''-------------------------------------------------------------------------------------------------------'''

'''                                             IMPORTS                                                   '''

'''-------------------------------------------------------------------------------------------------------'''

from py2neo import Graph as pGraph

from py2neo import Node as pNode

from py2neo import Relationship as pRelationship

from collections import defaultdict, deque

import igraph

import sys

import timeit

import psycopg2

# import warnings
# warnings.filterwarnings("error")



road_point_label = "RoadPoint"
road_segment_name = "ROAD_SEGMENT"
vehicle_label = "Vehicle"
vehicle_start_name = "START_AT"
vehicle_end_name = "END_AT"

'''-------------------------------------------------------------------------------------------------------'''

'''                                   CLASS AND METHOD DEFINITION                                         '''

'''-------------------------------------------------------------------------------------------------------'''

class PlatoonRoute:

    def __init__(self):

        self.trucks = []

        self.start_node = Node()

        self.end_node = Node()

        self.totalWeight=0

        self.sharedEdges=[]



    def __init__(self,trucks, startNode, endNode, totalWeight, sharedEdges):

        self.trucks = trucks

        self.start_node = startNode

        self.end_node = endNode

        self.totalWeight = totalWeight

        self.sharedEdges = sharedEdges



    def add_truck(self, truck):

        self.trucks.append(truck)



    def printOut(self):

        print("Platoon starts at:")

        print(self.start_node)

        print("Platoon ends at:")

        print(self.end_node)

        counter=0

        for truck in self.trucks:

            counter+=1

            print("Truck " + str(counter) + " " + truck.getPathDescription())





class Truck:

    def __init__(self):

        self.start = Node()

        self.destination = Node()

        self.distance = 0

    def __init__(self, start, destination, distance):

        self.start = start

        self.destination = destination

        self.distance = distance



    def getPathDescription(self):

        return("starts at " + str(self.start) + " and drives to " + str(self.destination) + " over a distance of " + str(self.distance))



savingsFactor=0.1;

#problems with directed edges!!!





def hubHeuristic(graph, startDests):

    print("Starting Hub-Heuristic")



    print("Initializing platoons")

    platoons = []

    trucks = []

    '''

    ---------------------------------------------------------------------------------------------------------------------------------

                                                INITIALIZING TRUCKS

    ---------------------------------------------------------------------------------------------------------------------------------

    '''

    for startDest in startDests:

        shortestPath = graph.shortest_paths_dijkstra(startDest[0], startDest[1], "weight", "ALL")[0][0]

        truck = Truck(startDest[0], startDest[1], shortestPath)

        trucks.append(truck)



    '''

    ---------------------------------------------------------------------------------------------------------------------------------

                                                FETCHING EDGE RATINGS

    ---------------------------------------------------------------------------------------------------------------------------------

    '''
    print("Fetching edge ratings")
    eRatings={}


    edgeRatingIterationCounter = 0
    for truck in trucks:
        edgeRatingIterationCounter += 1
        eRatings[(truck.start, truck.destination)] = getEdgeRating(graph, [truck.start, truck.destination])
        if(printMode=="ALLINFO"):
            print("Finished edge rating " + str(edgeRatingIterationCounter) + " of " + str(len(trucks)))

    print("Finished retrieving edge ratings")


    '''

    ---------------------------------------------------------------------------------------------------------------------------------

                                                INITIALIZING PLATOONS

    ---------------------------------------------------------------------------------------------------------------------------------

    '''
    print("Initializing platoons")
    for truck in trucks:

        platoon = PlatoonRoute([truck], truck.start, truck.destination, truck.distance, eRatings[(truck.start, truck.destination)])

        platoons.append(platoon)





    '''

    ---------------------------------------------------------------------------------------------------------------------------------

                                                USING EDGE RATINGS TO MERGE PLATOONS

    ---------------------------------------------------------------------------------------------------------------------------------

    '''
    print("Using edge ratings to merge platoons")
    merging=True

    mergingIterationCounter = 0

    while(merging):
        if (printMode == "ALLINFO"):
            print("Merging iteration: " + str(mergingIterationCounter))
        mergingIterationCounter += 1
        matching = ()

        matchingGrade = 0

        merging=False

        for platoon1 in platoons:

            for platoon2 in platoons:

                if(platoon1 != platoon2):

                    currentMatchingGrade=0

                    allTrucks = platoon1.trucks + platoon2.trucks

                    for edge in platoon1.sharedEdges:

                        if(edge in platoon2.sharedEdges):

                            matchingGain=platoon1.sharedEdges[edge]["weight"]*(1-((len(platoon1.trucks) + len(platoon2.trucks)-1)*savingsFactor))

                            detourMalus=0

                            for truck in allTrucks:

                                detourMalus+=eRatings[(truck.start, truck.destination)][edge]["rating"]

                            matchingGain -= detourMalus

                            if(matchingGain>0):

                                currentMatchingGrade+=matchingGain

                    if((currentMatchingGrade>matchingGrade) and (currentMatchingGrade>0)):

                        matchingGrade=currentMatchingGrade

                        matching=(platoon1, platoon2)

                        merging=True



        '''

        ---------------------------------------------------------------------------------------------------------------------------------

                                                                    FINDING HUB

        ---------------------------------------------------------------------------------------------------------------------------------

        '''
        print("finding hubs")


        if(merging):

            platoons.remove(matching[0])

            platoons.remove(matching[1])

            commonEdges = {}

            for edge in matching[0].sharedEdges:

                if(edge in matching[1].sharedEdges):

                    commonEdges[edge]=matching[0].sharedEdges[edge]

            newPlatoon = PlatoonRoute(matching[0].trucks + matching[1].trucks, None, None, matching[0].totalWeight + matching[1].totalWeight, commonEdges)

            platoons.append(newPlatoon)



    '''

    ---------------------------------------------------------------------------------------------------------------------------------

                                            FINDING BEST  MERGING AND SPLITTING POINT

    ---------------------------------------------------------------------------------------------------------------------------------

    '''

    print("finding best merging and splitting point")

    splitUpTrucks= []

    splitUpPlatoons = []

    platoonIterationCounter = 0
    for platoon in platoons:
        platoonIterationCounter += 1
        if (printMode == "ALLINFO"):
            print("Checking platoon " + str(platoonIterationCounter))
        bestValue = sys.maxsize

        bestStart = None

        bestDest = None
        edgePairIterationCounter = 0
        for edge1 in platoon.sharedEdges:

            for edge2 in platoon.sharedEdges:
                edgePairIterationCounter += 1
                if (printMode == "ALLINFO"):
                    print("Checking edge pair " + str(edgePairIterationCounter) + " for platoon Nr. " + str(platoonIterationCounter))
                platoonStart = edge1[0]

                platoonDestination = edge2[1]

                currentValue = 0

                betweenDistance = graph.shortest_paths_dijkstra(platoonStart, platoonDestination)[0][0]*(1+((1-savingsFactor)*(len(platoon.trucks)-1)))

                for truck in platoon.trucks:

                    intoPlatoon = graph.shortest_paths_dijkstra(truck.start, platoonStart)[0][0]

                    outOfPlatoon = graph.shortest_paths_dijkstra(platoonDestination, truck.destination)[0][0]

                    currentValue += intoPlatoon + betweenDistance + outOfPlatoon



                if(currentValue<bestValue):

                    bestStart = platoonStart

                    bestDest = platoonDestination

                    bestValue=currentValue

        platoon.start_node = bestStart

        platoon.end_node = bestDest



        if(platoon.start_node == platoon.end_node):

            splitUpPlatoons.append(platoon)

            for truck in platoon.trucks:

                splitUpTrucks.append(PlatoonRoute([truck], truck.start, truck.destination, truck.distance, None))



    '''

    ---------------------------------------------------------------------------------------------------------------------------------

                                            REMOVING BAD PLATOONS

    ---------------------------------------------------------------------------------------------------------------------------------

    '''





    for brokenPlatoon in splitUpPlatoons:

        platoons.remove(brokenPlatoon)



    for singleTruckPlatoon in splitUpTrucks:

        platoons.append(singleTruckPlatoon)



    return platoons







def getEdgeRating(graph, startDest):


    sp = saveShortestPaths(graph, startDest[0], startDest[1])
    if(sp==None):
        raise Exception('The shortest path for the Truck ' + str(startDest) + ' could not be traversed!')



    minimalWeight=0

    shortestPath={}

    for edge in sp[0]:

        source = graph.es[edge].source

        target = graph.es[edge].target

        key = (graph.vs[source]["name"], graph.vs[target]["name"])

        shortestPath[key]={"rating":0, "weight":graph.es[edge]["weight"]}

        minimalWeight+=graph.es[edge]["weight"]



    edgeRatings = dict(shortestPath);

    for vertex in graph.vs:
        r1 = saveShortestPaths(graph, startDest[0], vertex)
        r2 = saveShortestPaths(graph, vertex, startDest[1])

        #print(r1)
        #print(r2)
        if(r1 != None and r2 != None):
            toV = r1[0]
            fromV = r2[0]
            edgeList = toV + fromV;



            totalWeight = 0
            try:
                for edge in edgeList:

                    totalWeight += igraph.es[edge]["weight"]



                if (totalWeight*(1-savingsFactor) < minimalWeight):

                    lastNodeName = startDest[0]

                    for index in range(0, len(edgeList)):

                        if (lastNodeName == graph.vs[graph.es[edgeList[index]].source]["name"]):

                            source = graph.es[edgeList[index]].source

                            target = graph.es[edgeList[index]].target

                        else:

                            source = graph.es[edgeList[index]].target

                            target = graph.es[edgeList[index]].source

                        sourceName = graph.vs[source]["name"]

                        targetName = graph.vs[target]["name"]



                        lastNodeName = targetName



                        weightDeviation = totalWeight - minimalWeight

                        if((sourceName, targetName) in edgeRatings):

                            if(edgeRatings[(sourceName, targetName)]["rating"]>weightDeviation):

                                edgeRatings[(sourceName, targetName)]={"rating":weightDeviation, "weight":graph.es[edgeList[index]]["weight"]}

                        else:

                            edgeRatings[(sourceName, targetName)]={"rating":weightDeviation, "weight":graph.es[edgeList[index]]["weight"]}
            except:
                print("Some mysterious python-version specific error occured")
    return edgeRatings




#filtering out errors from igraph when a vertex cannot be reached
def saveShortestPaths(graph, vFrom, vTo):
    problemoccured = False
    try:
        try:
            result = graph.get_shortest_paths(vFrom, vTo, "weight", "ALL", "epath")
            if(len(result)==0 or len(result[0])==0):
                problemoccured = True
        except RuntimeWarning:
            #print("RUNTIMEWARNING")
            pass
    except:
        problemoccured = True
        #print("problem caught")
    if(problemoccured):
        return None
    else:
        return result






'''-------------------------------------------------------------------------------------------------------'''

'''                                           ACTUAL CODE                                                 '''

'''-------------------------------------------------------------------------------------------------------'''


printMode="NONE" #ALLINFO

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





"""CONNECTING AND FETCHING DATA"""

g = igraph.Graph(1)

#connects to the neo4j database and authorises with neo4j:12345678

print("Connecting to the database")

graph = pGraph("http://neo4j:12345678@localhost:7474/db/data/")

print("Successfully connected")





trucks = []

startDestinationDicts = graph.run("MATCH (start)<-[s:" + str(vehicle_start_name) + "]-(v:" + str(vehicle_label) + ")-[d:" + str(vehicle_end_name) + "]->(destination) RETURN id(start), id(destination) LIMIT " + str(limit)).data()

print(startDestinationDicts)

for startDestinationDict in startDestinationDicts:

    trucks.append([str(startDestinationDict["id(start)"]), str(startDestinationDict["id(destination)"])])

print(trucks)





neighbours = []

print("Fetching distance-edges from database")

neighbours = graph.run("MATCH (a:"+ str(road_point_label) + ")-[r:" + str(road_segment_name) + "]->(b:" + str(road_point_label) + ") RETURN id(a), id(b), r.distance").data()


edges = []

for edge in neighbours:

    edges.append([str(edge['id(b)']), str(edge['id(a)']), edge["r.distance"]])


igraph = igraph.Graph.TupleList(edges, False, "name", None, True)



start = timeit.default_timer()

platoons = hubHeuristic(igraph, trucks)

stop = timeit.default_timer()






resultRuntime = stop-start



resultWeightSum = 0

counter = 0

for platoon in platoons:

    counter+=1

    print("Platoon number " + str(counter))

    print("--------------")

    platoon.printOut()

    print("              ")

    inBetween = igraph.shortest_paths_dijkstra(platoon.start_node, platoon.end_node, "weight", "ALL")[0][0] * ((1 + ((1 - savingsFactor) * (len(platoon.trucks) - 1))) / len(platoon.trucks))

    for truck in platoon.trucks:

        pathIn = igraph.shortest_paths_dijkstra(truck.start, platoon.start_node, "weight", "ALL")[0][0]

        pathOut = igraph.shortest_paths_dijkstra(platoon.end_node, truck.destination, "weight", "ALL")[0][0]

        weightSum = pathIn + inBetween + pathOut

    resultWeightSum+=weightSum



resultWeight=0

for truck in trucks:

    shortestPath = igraph.shortest_paths_dijkstra(truck[0], truck[1])[0][0]

    resultWeight+=shortestPath



print("Total weight before using the Hub heuristic: " +str(resultWeight))

print("Total weight after using the Hub heuristic: " + str(resultWeightSum))

print("Calculated within a runtime of: " + str(resultRuntime) + " seconds")





cedges = len(neighbours)



sql = " BEGIN; INSERT INTO hubheuristic (objectiveValue, time, testid, shortestpath) VALUES ('" + str(resultWeightSum) + "', '" + str(resultRuntime) + "', '" + str(testid) + "', '" + str(resultWeight)+ "'); COMMIT;"



if log:

    try:

        connection = psycopg2.connect("dbname='platoon' user='admin' host='139.174.101.155' port=5432 password='admin123'")

        with connection.cursor() as cursor:

            res = cursor.execute(sql)

            print(sql)

    except:

        print("I am unable to connect to the database")

    finally:

        connection.close()
