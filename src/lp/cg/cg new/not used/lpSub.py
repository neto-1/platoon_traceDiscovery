from gurobipy import *
import networkx as nx
from route import Route
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client

outputControlValues = False

def subTwoVeh(allVehicles, group, G, saving, indexRoute):
    count = 0
    for veh in group:

        for veh2 in group:

            # exclude the same vehicles
            if veh == veh2:
                continue
            # only one comparison of two vehicles (veh and veh2, not veh2 and veh)
            if veh < veh2:

                # create a list of both vehicle objects
                twoVehicles = []
                for vehicle in allVehicles:
                    if (vehicle.getID() == veh or vehicle.getID() == veh2):
                        twoVehicles.append(vehicle)

                # run the sub problem and find bestpair of veh and veh2
                (valSub, path, dista, nodesPa) = lpSub.lpSubTwoVeh(twoVehicles, G, saving)
                # count the number of iterations of the subproblem run
                count += 1

                for vehi in twoVehicles:
                    # increase the index counter for routes (always before creating a new route!!
                    indexRoute += 1

                    # create a route with ID, edges and distance
                    route = Route(indexRoute, dista[vehi.getID()], path[vehi.getID()], nodesPa[vehi.getID()])

                    # add the path to the routes of the vehicle
                    vehi.addPath(route)

    #### check if the sub problem will run the right amount of times
    # calculate the number of times, the sub problem should run
    neededIterationsSub = ((len(group)*(len(group)-1))/2)
    if count < neededIterationsSub:
        print("!!!!!!ERROR!!!!!!")
        print("the subproblem hasn't run enough times: it ran " + str(count) + " times and should have run " + str(len(group)) + " times")
    if count > neededIterationsSub:
        print("!!!!!!ERROR!!!!!!")
        print("the subproblem has run too many times: it ran " + str(count) + " times and should have run " + str(len(group)) + " times")
    ### output for iteration control variable
    if outputControlValues:
        print("this should be n(n-1)/2 for n vehicles: " + str(count))
        print("group" + str(group))

    # the index have to be returned for the next current number
    return indexRoute



def lpSubTwoVeh(vehicles, G, saving):
    # LP
    mSub = Model("Platooning")
    mSub.setParam("OutputFlag", False)

    # Assoz. array - dict
    x = {}
    y = {}

    for e in G.edges():
        x[e] = {}
        y[e] = mSub.addVar(vtype=GRB.BINARY, obj=saving*G[e[0]][e[1]]['c'])
        for h in vehicles:
            x[e][h.getID()] = mSub.addVar(vtype=GRB.CONTINUOUS, lb = 0, obj=(1-saving)*G[e[0]][e[1]]['c'])
    mSub.update()

    for v in G.nodes():
        for h in vehicles:
            if v == h.getStart():
                b = 1
            elif v == h.getEnd():
                b = -1
            else:
                b = 0
            mSub.addConstr(quicksum(x[e][h.getID()] for e in G.out_edges(v)) - quicksum(x[e][h.getID()] for e in G.in_edges(v)) == b)

    for e in G.edges():
        for h in vehicles:
            mSub.addConstr(x[e][h.getID()] <= y[e])

    #m.setObj()
    mSub.optimize()
   # print(m.Objval)
   # print(m.status)


    # create new dict for the path o fboth vehicles
    pa = {}
    dista = {}
    nodesPa = {}
    for veh in vehicles:
        edgesInPath = []
        distanceInPath = []
        nodesInPath = []

        for e in G.edges():
            if x[e][veh.getID()].X> 0.9:
                edgesInPath.append(G[e[0]][e[1]]['id'])
                distanceInPath.append(G[e[0]][e[1]]['c'])
                nodesInPath.append(e)

        pa[veh.getID()] = edgesInPath
        dista[veh.getID()] = distanceInPath
        nodesPa[veh.getID()] = nodesInPath


    return (mSub.ObjVal, pa, dista, nodesPa)