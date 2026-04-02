from py2neo import Graph as pGraph
from py2neo import Node as pNode
from py2neo import Relationship as pRelationship
from collections import defaultdict, deque
import sys
import igraph
import timeit


'''                                   CLASS AND METHOD DEFINITION                                         '''


savingFactor = 0.1
road_point_label = "RoadPoint"
road_segment_name = "ROAD_SEGMENT"
vehicle_label = "Vehicle"
vehicle_start_name = "START_AT"
vehicle_end_name = "END_AT"


class PlatoonRoute:

    def __init__(self, trucks, start_node, end_node, total_weight, igraph):
        self.trucks = trucks
        self.start_node = start_node
        self.end_node = end_node
        self.graph = igraph
        self.total_weight = total_weight
        self.shortestPathWeight = self.getShortestPathValue()
    '''
    def __init__(self, trucks, startNode, endNode, total_weight, sharedEdges, igraph):
        self.trucks = trucks
        self.start_node = startNode
        self.end_node = endNode
        self.sharedEdges = sharedEdges
        self.graph = igraph
        self.total_weight = total_weight
        self.shortestPathWeight = self.getShortestPathValue()
    '''
    def add_truck(self, truck):
        self.trucks.append(truck)

    def set_start_node(self, start_node):
        self.start_node = start_node

    def set_end_node(self, end_node):
        self.end_node = end_node

    def print_out(self):
        print("Platoon starts at:")
        print(self.start_node)
        print("Platoon ends at:")
        print(self.end_node)
        counter = 0
        for truck in self.trucks:
            counter += 1
            print("Truck " + str(counter) + " " + truck.get_path_description())

    def updateTotalWeight(self):
        igraph = self.graph
        self.total_weight = self.getTotalWeight()
        return self.total_weight

    def getTotalWeight(self):
        result_weight = 0
        igraph = self.graph
        inBetween = igraph.shortest_paths_dijkstra(self.start_node, self.end_node, "weight", "ALL")[0][0] * ((1 + ((1 - savingsFactor) * (len(self.trucks) - 1))) / len(self.trucks))
        for truck in self.trucks:
            pathIn = igraph.shortest_paths_dijkstra(truck.start, self.start_node, "weight", "ALL")[0][0]
            pathOut = igraph.shortest_paths_dijkstra(self.end_node, truck.destination, "weight", "ALL")[0][0]
            weight_sum = pathIn + inBetween + pathOut
            result_weight += weight_sum
        return result_weight

    def getShortestPathValue(self):
        igraph = self.graph
        resultValue = 0
        for truck in self.trucks:
            resultValue += igraph.shortest_paths_dijkstra(truck.start, truck.destination, "weight", "ALL")[0][0]
        return resultValue

    def getSavings(self):
        return self.shortestPathWeight - self.total_weight


class PlatoonMerge:
    def __init__(self, platoon1, platoon2):
        self.platoon1=platoon1
        self.platoon2=platoon2


class Truck:
    def __init__(self):
        self.start = Node()
        self.destination = Node()
        self.distance = 0

    def __init__(self, start, destination, distance):
        self.start = start
        self.destination = destination
        self.distance = distance

    def get_path_description(self):
        return "starts at " + str(self.start) + " and drives to " + str(self.destination) + " over a distance of " + str(self.distance)


def find_best_merging_and_splitting_point(platoon1, platoon2, graph):
    initial_total_weight = platoon1.total_weight + platoon2.total_weight
    old_total_weight = initial_total_weight
    trucks = platoon1.trucks + platoon2.trucks
    best_start_end_weight_savings = {}
    for v1 in graph.vs:  # iterate through all nodes
        for v2 in graph.vs:  # iterate through all nodes * nodes
            if v1["name"] != v2["name"]:  # if the nodes are not the same
                total_weight = 0
                in_between_platoon = graph.shortest_paths_dijkstra(v1, v2, "weight", "ALL")[0][0] * ((1 + ((1 - savingFactor) * (len(trucks) - 1))) / len(trucks))  # moved here for performance

                if in_between_platoon > old_total_weight:  # try boosting performance
                    continue

                for truck in trucks:
                    path_to_merge = graph.shortest_paths_dijkstra(truck.start, v1, "weight", "ALL")[0][0]
                    path_from_split = graph.shortest_paths_dijkstra(v2, truck.destination, "weight", "ALL")[0][0]
                    # inBetween = graph.shortest_paths_dijkstra(v1, v2, "weight", "ALL")[0][0] * ((1 + ((1 - savingFactor) * (len(trucks) - 1))) / len(trucks))
                    weight_sum = path_to_merge + in_between_platoon + path_from_split
                    total_weight += weight_sum
                if total_weight < old_total_weight:
                    old_total_weight = total_weight
                    best_start_end_weight_savings = {'start': v1["name"], 'end': v2["name"], 'totalWeight': total_weight, 'savings': initial_total_weight - total_weight}
    if best_start_end_weight_savings != []:
        return best_start_end_weight_savings
    else:
        return {}


# graph -> IGraph of the street network
# startDests -> list of lists representing a truck each, containing the name of the starting node as first and the name of the destination node as the second element
# returns a list of platoons
def best_pair_heuristic(graph, startDests):
    print("Starting Best Pair Heuristic")
    print(startDests)
    print("Initializing platoons")
    platoons = []
    trucks = []

    shortest_path_total_weight = 0

    # init trucks and init shortest paths distances to sum them up (for lower bound)
    for start_dest in startDests:
        shortest_path_truck = graph.shortest_paths_dijkstra(start_dest[0], start_dest[1], "weight", "ALL")[0][0]

        truck = Truck(start_dest[0], start_dest[1], shortest_path_truck)
        trucks.append(truck)
        shortest_path_total_weight += shortest_path_truck

    print("Total Weight when using the shortest path for every truck: " + str(shortest_path_total_weight))

    # init platoons (one for every truck)
    for truck in trucks:
        platoon = PlatoonRoute([truck], truck.start, truck.destination, truck.distance, graph)
        platoons.append(platoon)
        # print("Distance from " + truck.start + " to " + truck.destination + " is ")
        # print(truck.distance)

    itCounter = 0  # counts iterations

    # set a variable to true, so that the while loop finishes when no improvements can be found
    improvement_found = True
    platoon_merge_values = {}  # contains the saving values of platoon-merges addressed by a PlatoonMerge-Object as a key

    while improvement_found:
        itCounter += 1
        print("Iteration Nr.: " + str(itCounter))
        improvement_found = False
        for platoon1 in platoons:
            for platoon2 in platoons:
                already_compared = False #indicates whether two platoons have already been considered for merging

                for key in platoon_merge_values:

                    if (key.platoon1 == platoon1 and key.platoon2 == platoon2) or (key.platoon1 == platoon2 and key.platoon2 == platoon1):
                        already_compared = True
                if platoon1 != platoon2 and not already_compared:
                    value = find_best_merging_and_splitting_point(platoon1, platoon2, graph)
                    platoon_merge_values[PlatoonMerge(platoon1, platoon2)] = value
                    print(value)
        bestCurrentChoice = {'savings': 0}  # contains the best current choice of platoon merges
        for key in platoon_merge_values:
            if platoon_merge_values[key] != {} and bestCurrentChoice['savings'] < platoon_merge_values[key]['savings']:
                value = platoon_merge_values[key]
                bestCurrentChoice = {'savings': value['savings'], 'totalWeight': value['totalWeight'], 'start': value['start'], 'end': value['end'], 'platoons': [key.platoon1, key.platoon2]}
                improvement_found = True
        if bestCurrentChoice['savings'] > 0:
            oldPlatoons = bestCurrentChoice['platoons']
            platoons.remove(oldPlatoons[0])
            platoons.remove(oldPlatoons[1])
            newPlatoon = PlatoonRoute(oldPlatoons[0].trucks + oldPlatoons[1].trucks, bestCurrentChoice['start'], bestCurrentChoice['end'], bestCurrentChoice['totalWeight'], graph)
            platoons.append(newPlatoon)
            keysToDelete = []
            for key in platoon_merge_values:
                if key.platoon1 in oldPlatoons or key.platoon2 in oldPlatoons:
                    keysToDelete.append(key)
            for key in keysToDelete:
                del platoon_merge_values[key]

    return platoons

'''-------------------------------------------------------------------------------------------------------'''
'''                                           ACTUAL CODE                                                 '''
'''-------------------------------------------------------------------------------------------------------'''

limit = 9

if len(sys.argv) > 1:
    limit = sys.argv[1]
testid = -1

if len(sys.argv) > 2:

    testid = sys.argv[2]

if int(testid) > -1:
    log = True
else:

    log = False

"""CONNECTING AND FETCHING DATA"""
g = igraph.Graph(1)
# connects to the neo4j database and authorises with neo4j:12345678
print("Connecting to the database")
graph = pGraph("http://neo4j:12345678@localhost:7474/db/data/")
print("Successfully connected")


# startDestinationDicts = graph.run("MATCH (start)<-[s:STARTATLOCATION]-(v:veh)-[d:ENDATLOCATION]->(destination) RETURN start.name, destination.name").data()

startDestinationList = []

# normal graphs
startDestinationDicts = graph.run("MATCH (start)<-[s:" + str(vehicle_start_name) + "]-(v:" + str(vehicle_label) + ")-[d:" + str(vehicle_end_name) + "]->(destination) RETURN id(start), id(destination) LIMIT " + str(limit)).data()
# testing ingrid
# startDestinationDicts = graph.run("MATCH (start)<-[s:startAtLocation]-(v:vehicle)-[d:endAtLocation]->(destination) RETURN id(start), id(destination) LIMIT " + str(limit)).data()

print(startDestinationDicts)
print("-----------")

for startDestinationDict in startDestinationDicts:
    startDestinationList.append([str(startDestinationDict["id(start)"]), str(startDestinationDict["id(destination)"])])

print(startDestinationList)

neighbours = []

print("Fetching distance-edges from database")

neighbours = graph.run("MATCH (a:"+str(road_point_label)+")-[r:"+str(road_segment_name)+"]->(b:"+str(road_point_label)+") RETURN id(a), id(b), r.distance").data()

# gridnetwork:
# neighbours = graph.run("MATCH (a:location)-[r:neighbourEdges]->(b:location) RETURN id(a), id(b), r.distance").data()


edges = []

for edge in neighbours:

    edges.append([str(edge['id(b)']), str(edge['id(a)']), edge["r.distance"]])

print(edges)
igraph = igraph.Graph.TupleList(edges, False, "name", None, True)

pre_shortest_path = 0

for startDestination in startDestinationList:
    shortestPath = igraph.shortest_paths_dijkstra(startDestination[0], startDestination[1], "weight", "ALL")[0][0]
    pre_shortest_path += shortestPath

start_time_best_pair = timeit.default_timer()
platoons = best_pair_heuristic(igraph, startDestinationList)
end_time_best_pair = timeit.default_timer()

resultRuntime = end_time_best_pair - start_time_best_pair

resultWeightSum = 0
counter = 0
for platoon in platoons:
    counter+=1
    print("Platoon number " + str(counter))
    print("--------------")
    platoon.print_out()
    print("              ")
    resultWeightSum += platoon.total_weight

print("Total weight before using the Hub heuristic: " +str(pre_shortest_path))
print("Total weight after using the Best Pair heuristic: " + str(resultWeightSum))
print("Calculated within a runtime of: " + str(resultRuntime) + " seconds")

cedges = len(neighbours)

sql = " BEGIN; INSERT INTO hubheuristic (objectiveValue, time, testid) VALUES ('" + str(resultWeightSum) + "', '" + str(resultRuntime) + "', '" + str(testid) + "', '" + str(pre_shortest_path)+ "'); COMMIT;"


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
