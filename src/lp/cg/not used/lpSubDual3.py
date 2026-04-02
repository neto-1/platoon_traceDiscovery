from gurobipy import *
import networkx as nx
import lpSubDual
from route import Route

def lpSubDual3(vehicles, G, indexRoute, paths, vehicleShadowpPrices, edgeShadowPrices):
    foundNewPath = False
    redzielfunkcoeff = {}
    # iterate over all vehicles

    for veh in vehicles:
        # make an LP for every vehicle
        createRoute = Model("createRoute")
        createRoute.setParam("OutputFlag", False)
        createRoute.ModelSense = -1
        y = {} # binary variable, indicating if edge e is being used

        # only one variable in the objective
        for e in G.edges():
           # y[e] = createRoute.addVar(vtype=GRB.BINARY, obj= G[e[0]][e[1]]['c'] + vehicleShadowpPrices[veh.getID()][str(G[e[0]][e[1]]['id']) + " " + str(veh.getID())], name = str(G[e[0]][e[1]]['id']))
            y[e] = createRoute.addVar(vtype=GRB.CONTINUOUS, obj= -0.0001 - edgeShadowPrices[G[e[0]][e[1]]['id']], name = str(G[e[0]][e[1]]['id']))
           # vehicleShadowpPrices[veh.getID()][str(G[e[0]][e[1]]['id']) + str(veh.getID())]

        createRoute.update()


        # restraint: it has to be a path from start to end node
        for v in G.nodes():
            if v == veh.getStart():
                b = 1

            elif v == veh.getEnd():
                b = -1

            else:
                b = 0
            createRoute.addConstr(quicksum(y[e] for e in G.out_edges(v)) - quicksum(y[e] for e in G.in_edges(v)) == b)



        #createRoute.setObjective(quicksum(pi[i] * y2[i] for i in G.edges()), GRB.MAXIMIZE)
        createRoute.optimize()

        ### create route as an object
        route = []
        routeDistances = []

        sumOfaTimesu = 0


        for e in G.edges():
            if y[e].X > 0.99:

                route.append(G[e[0]][e[1]]['id'])
                routeDistances.append(G[e[0]][e[1]]['c'])
                sumOfaTimesu += y[e].X *edgeShadowPrices[G[e[0]][e[1]]['id']]


       # redzielf = (sum(routeDistances) - sumOfaTimesu) - vehicleShadowpPrices[veh.getID()]["path of : " + str(veh.getID())]
        redzielf = (sum(routeDistances) - sumOfaTimesu) - vehicleShadowpPrices[veh.getID()]["path of : " + str(veh.getID())]


        print("value of: " + str(redzielf) + " for veh: " + str(veh.getID()))



        if redzielf < 0:
            # increase route ID
            indexRoute += 1
            #create Route object
            newPath = Route(indexRoute, routeDistances, route)
            # add the path to the vehicle
            veh.addPath(newPath)

            #set the variable for the iteration of the main loop to true
            foundNewPath = True

        ################################### first try reduzierende zielfunktionkoeefizienten

       # print(resZielfunktionsKoeff)
        # c - a*u
        # distance - a * pi

        # add the new path to the vehicle




    return(indexRoute,redzielfunkcoeff, foundNewPath)