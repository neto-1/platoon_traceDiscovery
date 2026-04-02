from gurobipy import *
import networkx as nx
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time
import lppl

import createInitPaths
import lpMaster
import lpSub
import lpSubDual

from vehicle import Vehicle
from route import Route


############################ ===== INITIALIZATION ===== ############################
# this is true, if u wanna check the unnecessary outputs
outputControlValues = False
showOptSolution = True
showActualTest = False
actualMasterOpt = True
includeTwoVehSub = False


# the saving factor
saving = 0.1

#number of times the algorithm is correct (optVal = valMaster)
timesCorrectOptValue = 0

#number of times the algorithm isn't correct (optVal - valMaster > 0.001)
timesWrongOptValue = 0
# list of not working groups
notWorkingGroups = []

# save the initial time
time_init = time.clock()
# init the database
db = GraphDatabase("http://localhost:7474", username="neo4j", password="12345678")
#db = GraphDatabase("http://localhost:7474", username="neo4j", password="1234567890")
#query = "MATCH (g:Group)-[r:INGROUP]->(v:veh),(e:loc)-[:ENDATLOCATION]-(v)-[:STARTATLOCATION]-(s:loc)," \
#        "sp = shortestPath((s)-[:NEIGHBOUR *..150]-(e)) where length(sp) > 1 RETURN DISTINCT id(v), id(e), id(s)"


query = "MATCH (g:Group)-[r:INGROUP]->(v:veh),(e:loc)-[:ENDATLOCATION]-(v)-[:STARTATLOCATION]-(s:loc)" \
        "RETURN DISTINCT id(v), id(e), id(s)"
#query = "MATCH (g:Group)-[r:INGROUP]->(v:vehicle),(e:location)-[:endAtLocation]-(v)-[:startAtLocation]-(s:location)" \
#        "RETURN DISTINCT id(v), id(e), id(s)"

results = db.query(query)
results1 = results
#craete a list of all vehicles and a list for the starting and a list for the ending nodes
vehicles = []
s = {}
t = {}
for r in results:
    vehicles.append(r[0])
    s[r[0]] = r[2]
    t[r[0]] = r[1]


query = "MATCH (g:Group)-[r:INGROUP]->(v:veh) RETURN id(g), id(v)"
#query = "MATCH (g:Group)-[r:INGROUP]->(v:vehicle) RETURN id(g), id(v)"
results = db.query(query)

# with the data queried, create the groups of vehicles (or in other words, the sets of vehicles to test)
groups = {}
for r in results:
    groupId = r[0]
    vehicleId = r[1]
    if groupId not in groups:
        groups[groupId] = []
    groups[groupId].append(vehicleId)
print(groups)

time_init = time.clock() - time_init
time_start = time.clock()

# counting variable for index of Routes
indexRoute = 0

# create a empty list for all vehicles
allVehicles = []

#### create objects for every vehicle and save them to a list
for vehicle in vehicles:
    #new index for next route
    indexRoute += 1

    # create every vehicle as an object
    veh = Vehicle(db, vehicle, s[vehicle], t[vehicle])

    # append the vehicle to the list of vehicles
    allVehicles.append(veh)
########################################## ===== End of Initialization ===== ##########################################



p={}
groupInfo={}


########################################## ===== MAIN LOOP ===== ##########################################
###### iterate all groups: if there are no groups, every vehicle belongs to one group
for key, group in groups.iteritems():

    # output the actual group


    if len(group) < 3:
        continue
    print(group)




    print("--- %%% --- %%% --- %%% --- %%%%%% --- NEXT GROUP --- %%%%%% --- %%% --- %%% --- %%% ---")
    print("group: ", str(key), " with vehicles: " + str(group))

    ##### get the groups and the polygon of the group
    query = "MATCH (g:Group)-[:UNION]->(p:Polygon) WHERE id(g) = " + str(key) + " RETURN p.Poly"
    results = db.query(query)

    query = "WITH 'POLYGON(("
    for r in results:
        for i in range(0, len(r[0])):
            query = query + " " + str(r[0][i])
            if ((i % 2 != 0) & (i < (len(r[0]) - 1))):
                query = query + ", "
  #  query = query + "))' as polygon CALL spatial.intersects('geometry',polygon) YIELD node as n1 with n1 MATCH (n1)-[r:neighbourEdges]->(n2) RETURN id(n1), id(n2), r.distance, id(r)"
    query = query + "))' as polygon CALL spatial.intersects('geom',polygon) YIELD node as n1 with n1 MATCH (n1)-[r:NEIGHBOUR]->(n2) RETURN id(n1), id(n2), r.distance, id(r)"

    results = db.query(query)

    # create the graph for the group
    G = nx.DiGraph()
    for r in results:
        G.add_edge(r[0],r[1], {'c': r[2], 'id': r[3]})
        G.add_edge(r[1],r[0], {'c': r[2], 'id': r[3]+0.5})


    # output for optimal solution and shortest path solution of LP
    if showOptSolution:
        # create the optimal solution with LP
        (valOpt, pathsOpt, eidsOpt) = lppl.lp(group, G, s, t, saving)
        print("optimal solution for !!platooning!! (vehicle-ID: "+ str(group) + " with OptVal: " + str(valOpt))
       # set1 = set(eidsOpt[98])

        # create the shortest path of all vehicles with LP
        (valSP, pathsSP, eidsSP) = lppl.lp(group, G, s, t, 0)
        print("optimal solution for !!shortest path!! (vehicle-ID: " + str(group) + " with OptVal: " + str(valSP))


    # create a list of all vehicle objects in this group
    groupVehicles = []

    #create a variable which saves the sum of all shortest path for this group
    sumOfShortestPath = 0



    ######################################## Initial Path creating ########################################
    ## only create shortest Path as initial paths
    indexRoute = createInitPaths.ShortestPath(allVehicles, indexRoute, s, t, db)

    ## create best path of repectively two vehicles of the set of vehicles considered
    indexRoute = lpSub.subTwoVeh(allVehicles, group, G, saving, indexRoute)
    ###################################### End Initial Path creating ######################################

    #### initially save the vehicle objects to a group and save the sum of shortest paths
    for HDV in group:
        # create a list for all vehicles-objects in that group
        for vehObjects in allVehicles:
            # add the vehicle to the actual group "groupVehicles"
            if vehObjects.getID() == HDV:
                groupVehicles.append(vehObjects)
                # add the shortest path to the sum of shortest paths
                sumOfShortestPath += sum(vehObjects.getPaths()[0].getDistance())






###################################### MAIN ITERAATION OF COLUMN GENERATION ######################################
    # create a cancel condition (this counts upwards, so that there are only maxIterations
    iterationOfMain = 0
   # maxIterations = 3
    # cancel condition which checks, if there is a new path generated (initially true)
    foundNewPath = True

    # create empty lists, to save the objectives and the paths of the objectives
    Objectives = []
    pathOfObjective = []

    ################------------------ %% SUB problem with 2 vehicles %% -------------------################
    #### create also the bestPair Path of 2 vehicles respectively
    if includeTwoVehSub:
        # add the respectively platoon path of 2 vehicles to the initial set of routes

        # only return is the index of the routes, which will always increased
        indexRoute = lpSub.subTwoVeh(groupVehicles, group, G, saving, indexRoute)
    ################ ------------------ %% SUB problem with 2 vehicles %% -------------------################


    while foundNewPath:

        # count the number of iterations
        iterationOfMain += 1

        ###################### run the master problem ######################
        (valMaster, paths, vehicleShadowpPrices) = lpMaster.lpMaster(groupVehicles, G, saving)
        if actualMasterOpt:
            print("------ %% the vehicle id and the respectively path of the optimal solution: ( " + str(
                valMaster) + " ) %% ------")
           # print(paths)


        #save the actual obj and path
        Objectives.append(valMaster)
        pathOfObjective.append(paths)


        #run the dual sub problem
        (indexRoute, foundNewPath) = lpSubDual.lpSubDual(groupVehicles, G, indexRoute, vehicleShadowpPrices)


    ##############################################################################################################


    shortestPathValue = 0
    query = "MATCH (g:Group)-[r:INGROUP]->(v:veh) WHERE id(g)= " + str(key) + "  RETURN sum(v.SP) as sp"
    #query = "MATCH (g:Group)-[r:INGROUP]->(v:vehicle) WHERE id(g)= " + str(key) + "  RETURN sum(v.SP) as sp"
    results = db.query(query);

    for r in results:
        shortestPathValue = r[0]
    if outputControlValues:
        if (shortestPathValue - sumOfShortestPath) < 0.00001:
            print("shortestPath is computed normally")
        else:
            print("---------------- %% ERROR %% ----------------")
            print("Error with shortest path")
            print("Because " + str(shortestPathValue) + " is not the same as " + str(sumOfShortestPath))
    shortestPathValue = sumOfShortestPath
    p[key] = shortestPathValue - valMaster
    savings = (p[key]*100/(shortestPathValue))

    print("savings group " + str(key) + ":", p[key], " SP: " + str(shortestPathValue) + " PSP: " + str(valMaster) + " savings(in %): " + str(savings) + " after " + str(iterationOfMain) + " iterations")
    groupInfo[key] = [p[key], shortestPathValue, valMaster, (p[key]*100/(shortestPathValue))]


    if outputControlValues:
        print("----------------------------------- %%% output of the vehicle and route objects %%% -----------------------------------")
        for veh in allVehicles:
            print("veh ID: " + str(veh.getID()))

            print("---veh-routen---")

            for routen in veh.getPaths():
                print("route id" + str(routen.getRouteID()))
                if len(routen.getDistance()) == len(routen.getPath()):
                    print("distance and route vektor are the same length")
                else:
                    print("ERRROR!!! not same length in distance and path")
                print("route and distance")
                print(routen.getPath())
                print(routen.getDistance())

                print("sum:  " + str(sum(routen.getDistance())))
    print("--------------- %%%%%%%%% output objectives %%%%%%%%% ---------------")

    print("master objectives")
    print(Objectives)
    print(valOpt)
    print("path in the master")
    print(pathOfObjective)
    print("Gap " + str(valMaster - valOpt))
    if valMaster - valOpt< 0.001:
        timesCorrectOptValue += 1
    else:
        print("ERRROR!!! NOT THE OPTIMAL PATHS! ----------------------------------------------------------------------------------------------------------------------------------------------------")
        timesWrongOptValue += 1
        notWorkingGroups.append(key)

    #delete the calculated paths of all vehicles in the group to start new
    for vehicle in allVehicles:
        vehicle.deletePaths()

print("the algorithm worked for " + str(timesCorrectOptValue) + " and didnt worked " + str(timesWrongOptValue) + " times")
print("percentage of right times: " + str(100*timesCorrectOptValue/ (timesCorrectOptValue+ timesWrongOptValue)) + "% ")
print("the not working group IDs are: " + str(notWorkingGroups))
time_elapsed = (time.clock() - time_start)

print("elapsed time in sec: " + str(time_elapsed))
