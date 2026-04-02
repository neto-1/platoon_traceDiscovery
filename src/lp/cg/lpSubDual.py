from gurobipy import *
from route import Route


def subproblem_dual_lp(vehicles, graph, index_route, vehicle_shadow_prices):
    found_new_path = False

    # save the real graph, so that after every vehicle iteration the real graph can be loaded
    # copy_of_real_graph = graph.copy()

    # iterate over all vehicles
    for veh in vehicles:

        # if a new path has been found, cancel and go for the master
        # if found_new_path:
        #    continue

        # load the real graph
        # graph = copy_of_real_graph.copy()

        # if the new path is the same as an already existing,
        # set this to true, so that it wont be added to the set pf paths
        same_path = False

        # create a graph with reduced costs for vehicle x,
        # all dual prices of all other vehicles are subtracted except for the dual prices of x
        # for e in graph.edges():
        #     for other_veh in vehicles:
        #         if vehicle_shadow_prices[other_veh.getID()][str(e) + " " + str(other_veh.getID())]\
        #                 != 0 and not(veh.getID() == other_veh.getID()):
        #             graph[e[0]][e[1]]['c'] = graph[e[0]][e[1]]['c'] -\
        #                                      vehicle_shadow_prices[other_veh.getID()][str(e) + " " +
        #                                                                               str(other_veh.getID())]

        # start the optimization process with the updated graph
        create_route = Model("create_route")
        create_route.setParam("OutputFlag", False)
        create_route.ModelSense = 1
        y = {}  # binary variable, indicating if edge e is being used

        # only one variable in the objective: the weight of the traveled edges
        for e in graph.edges():
            if str(e) in vehicle_shadow_prices['edge_list']:
                y[e] = create_route.addVar(vtype=GRB.BINARY,
                                           obj=graph[e[0]][e[1]]['c'] - quicksum(
                                               vehicle_shadow_prices[vehicle_id.getID()].get(str(e),
                                                                                             float(0)) for
                                               vehicle_id in
                                               vehicles).getValue() + vehicle_shadow_prices[veh.getID()].get(str(e),
                                                                                                             float(0)))
            else:
                y[e] = create_route.addVar(vtype=GRB.BINARY, obj=graph[e[0]][e[1]]['c'])
        create_route.update()

        # constraint: it has to be a path from start to end node
        for v in graph.nodes():
            if v == veh.getStart():
                b = 1

            elif v == veh.getEnd():
                b = -1

            else:
                b = 0
            create_route.addConstr(quicksum(y[e] for e in graph.out_edges(v))
                                   - quicksum(y[e] for e in graph.in_edges(v)) == b)

        # optimize the lp
        create_route.optimize()

        # ========== create route as an object =====
        # the list of the edgeIds
        route = []
        # the list of the distances per edge
        route_distances = []
        # the list of the nodes on the path
        route_nodes = []
        # variable for decide if the new path is worthy
        atimesu = 0

        # check if the new path would make a better OptVal in the master problem
        for e in graph.edges():
            if y[e].X > 0.99:
                # create route with IDs of the edges
                route.append(graph[e[0]][e[1]]['id'])
                # create a list of the distances
                route_distances.append(graph[e[0]][e[1]]['c'])
                # create a ordered list of the path with every edge displayed as two nodes
                route_nodes.append(e)

                # calculate a times u for the decision of including the route to the set of routes of the vehicle
                for other_veh in vehicles:
                    if veh.getID() != other_veh.getID() and e in vehicle_shadow_prices['edge_list']:
                        print(e)
                        atimesu += y[e].X * vehicle_shadow_prices[other_veh.getID()][str(e) + " " +
                                                                                     str(other_veh.getID())]

        # check if the path is already in the set of paths of the vehicle
        set1 = set(route)
        for tours in veh.getPaths():
            set2 = set(tours.getPath())
            # if the differences in both sets to each other are 0, then its the same path
            if len(set1.difference(set2)) == 0 and len(set2.difference(set1)) == 0:
                same_path = True

        if not same_path:
            # print("not same path here")
            # check if the new path has a better solution for the master problem
            reduction_coefficient = sum(route_distances) - (1/0.9)*(atimesu + vehicle_shadow_prices[veh.getID()]["path of : " + str(veh.getID())])
            # print(reduction_coefficient)
            if reduction_coefficient < 0.0000001:
                # print("new path here")
                # increase route ID
                index_route += 1
                # create Route object
                new_path = Route(index_route, route_distances, route, route_nodes)
                # add the path to the vehicle
                veh.addPath(new_path)
                # set the variable for the iteration of the main loop to true
                found_new_path = True

    return index_route, found_new_path
