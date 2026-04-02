from gurobipy import *
from route import Route

outputControlValues = False


def shortest_path(all_vehicles, index_route, s, t, db):
    for vehicle in all_vehicles:
        # new index for next route
        index_route += 1

        # get the shortest path
        query = 'call proceduretest.aStarPlugin(' + str(s[vehicle.getID()]) + ', ' + str(t[vehicle.getID()]) \
                + ', "distance", "lat", "lon", "coordinates", ["NEIGHBOUR"], [], [], "both") yield path  WITH ' \
                  ' path, extract(n IN relationships(path) | id(n)) as idn, extract(r IN relationships(path)' \
                  ' | r.distance) as distance, extract(m IN nodes(path) | id(m)) as idm return idn, distance, idm'
        res = db.query(query)

        # create a list of the edges through the nodes
        edge_list_of_nodes = list()
        for nodes in range(1, len(res[0][2])):
            edge_list_of_nodes.append((res[0][2][nodes - 1], res[0][2][nodes]))

        # create a route object for every route
        shortest_path_of_vehicle = Route(index_route, res[0][1], res[0][0], edge_list_of_nodes)

        # add the shortestPath-Route to the routes of the vehicle
        vehicle.addPath(shortest_path_of_vehicle)

    return index_route


def sub_best_pair_lp(all_vehicles, group, graph, saving, index_route):
    count = 0
    for veh in group:
        for veh2 in group:
            # only one comparison of two vehicles (veh and veh2, not veh2 and veh)
            if veh < veh2:

                # create a list of both vehicle objects
                two_vehicles = []
                for vehicle in all_vehicles:
                    if vehicle.getID() == veh or vehicle.getID() == veh2:
                        two_vehicles.append(vehicle)

                # run the sub problem and find bestpair of veh and veh2
                (valSub, path, distance, nodesPa) = lp_sub_two_vehicles(two_vehicles, graph, saving)
                # count the number of iterations of the subproblem run
                count += 1

                for vehi in two_vehicles:
                    # increase the index counter for routes (always before creating a new route!!
                    index_route += 1

                    # create a route with ID, edges and distance
                    route = Route(index_route, distance[vehi.getID()], path[vehi.getID()], nodesPa[vehi.getID()])

                    # add the path to the routes of the vehicle
                    vehi.addPath(route)

    # the index have to be returned for the next current number
    return index_route


def lp_sub_two_vehicles(vehicles, graph, saving):
    # LP
    model_sub = Model("Platooning")
    model_sub.setParam("OutputFlag", False)

    # Assoz. array - dict
    x = {}
    y = {}

    # create objective function
    for e in graph.edges():
        x[e] = {}
        y[e] = model_sub.addVar(vtype=GRB.BINARY, obj=saving * graph[e[0]][e[1]]['c'])  # , name=str(e))
        for h in vehicles:
            x[e][h.getID()] = model_sub.addVar(vtype=GRB.CONTINUOUS, lb=0, obj=(1 - saving) * graph[e[0]][e[1]]['c'],
                                               name=str(e))
    model_sub.update()

    # create the constraint for flow condition of vehicles
    for v in graph.nodes():
        for h in vehicles:
            if v == h.getStart():
                b = 1
            elif v == h.getEnd():
                b = -1
            else:
                b = 0
            model_sub.addConstr(quicksum(x[e][h.getID()] for e in graph.out_edges(v)) - quicksum(
                x[e][h.getID()] for e in graph.in_edges(v)) == b)

    # create constraint for "buying" the edges
    for e in graph.edges():
        for h in vehicles:
            model_sub.addConstr(x[e][h.getID()] <= y[e])

    # create constraint to let the two vehicles drive together over min one edge
    model_sub.addConstr(quicksum(x[e][vehicles[0].getID()] + x[e][vehicles[1].getID()] for e in graph.edges())
                        >= quicksum(y[e] for e in graph.edges()) + 1)

    # enable lazy constraints
    model_sub.params.LazyConstraints = 1
    # declare variables
    model_sub._var = model_sub.getVars()
    # optimize
    model_sub.optimize()

    # create new dict for the path of both vehicles
    path_of_vehicles = {}
    distances_in_veh_path = {}
    nodes_of_path = {}
    for veh in vehicles:
        edges_in_path = []
        distances_in_path = []
        nodes_in_path = []

        for e in graph.edges():
            if x[e][veh.getID()].X > 0.9:
                edges_in_path.append(graph[e[0]][e[1]]['id'])
                distances_in_path.append(graph[e[0]][e[1]]['c'])
                nodes_in_path.append(e)

        # formate for the output
        path_of_vehicles[veh.getID()] = edges_in_path
        distances_in_veh_path[veh.getID()] = distances_in_path
        nodes_of_path[veh.getID()] = nodes_in_path

    return model_sub.ObjVal, path_of_vehicles, distances_in_veh_path, nodes_of_path


def sub_best_pair_lp_callback(all_vehicles, group, graph, saving, index_route):
    # iterate through every pair of vehicles and add best pair path
    for veh in group:
        for veh2 in group:
            # only one comparison of two vehicles (veh and veh2, not veh2 and veh)
            if veh < veh2:

                # create a list of both vehicle objects
                two_vehicles = []
                for vehicle in all_vehicles:
                    if vehicle.getID() == veh or vehicle.getID() == veh2:
                        two_vehicles.append(vehicle)

                # run the sub problem and find best pair of veh and veh2
                (index_route) = \
                    lp_sub_two_vehicles_callback(two_vehicles, graph, saving, index_route)

    # the index have to be returned for the next current number
    return index_route


def lp_sub_two_vehicles_callback(vehicles, graph, saving, index_route):
    # define the callback function

    def new_tour(model, where):
        if where == GRB.Callback.MIPSOL:
            # print("init model with status")
            # print(model.status)
            # print("is it infeasibable or so")
            # print(str(hallo) + " ist der wahre status")
            # create routes for the two vehicles
            for vehicle in vehicles:
                edges_in_old_path = []
                distances_in_old_path = []
                nodes_in_old_path = []
                # get the edges used for the route
                for edge in graph.edges():
                    if model.cbGetSolution(x[edge][vehicle.getID()]) > 0.9:
                        edges_in_old_path.append(graph[edge[0]][edge[1]]['id'])
                        distances_in_old_path.append(graph[edge[0]][edge[1]]['c'])
                        nodes_in_old_path.append(edge)

                # increase the index counter for routes (always before creating a new route!!
                model_sub._index_route += 1
                # create a route with ID, edges and distance
                route = Route(model_sub._index_route, distances_in_old_path, edges_in_old_path, nodes_in_old_path)

                # add the path to the routes of the vehicle
                vehicle.addPath(route)

            # add the lazy constraint to the model
            for edge in graph.edges():
                if model.cbGetSolution(x[edge][vehicles[0].getID()]) > 0 \
                        and model.cbGetSolution(x[edge][vehicles[1].getID()]) > 0:
                    model_sub.cbLazy(y[edge] <= 0)

    # LP
    model_sub = Model("Platooning")
    model_sub.setParam("OutputFlag", False)

    # Association. array - dict
    x = {}
    y = {}

    # create objective function
    for e in graph.edges():
        x[e] = {}
        y[e] = model_sub.addVar(vtype=GRB.BINARY, obj=saving * graph[e[0]][e[1]]['c'])
        for h in vehicles:
            x[e][h.getID()] = model_sub.addVar(vtype=GRB.CONTINUOUS, lb=0, obj=(1 - saving) * graph[e[0]][e[1]]['c'])
    model_sub.update()

    # create the constraint for flow condition of vehicles
    for v in graph.nodes():
        for h in vehicles:
            if v == h.getStart():
                b = 1
            elif v == h.getEnd():
                b = -1
            else:
                b = 0
            model_sub.addConstr(quicksum(x[e][h.getID()] for e in graph.out_edges(v)) - quicksum(
                x[e][h.getID()] for e in graph.in_edges(v)) == b)

    # create constraint for "buying" the edges
    for e in graph.edges():
        for h in vehicles:
            model_sub.addConstr(x[e][h.getID()] <= y[e])

    # create constraint to let the two vehicles drive together over a minimal of one edge
    model_sub.addConstr(quicksum(x[e][vehicles[0].getID()] + x[e][vehicles[1].getID()]
                                 for e in graph.edges()) >= quicksum(y[e] for e in graph.edges()) + 1)

    # enable lazy constraints
    model_sub.params.LazyConstraints = 2
    # declare variables
    model_sub._var = model_sub.getVars()
    # store index of routes to the model
    model_sub._index_route = index_route
    # optimize
    model_sub.optimize(new_tour)
    # get the index of the actual route
    index_route = model_sub._index_route

    return index_route

# def relevant_paths(all_vehicles, index_route, s, t, db, allNames):
#     # query for all polygons of all vehicles
#     for vehicle in all_vehicles:
#         polygon = db.query("match (v:Vehicle)-[:HULL]-(p:Polygon) where id(v) = " +
# str(vehicle.getID()) + " return p.Poly")
#         # store the polygons in the object
#         vehicle.store_polygon(polygon[0][0])
#
#     # iterate all vehicle pairs
#     for vehicle in all_vehicles:
#         # store the relevant edges
#         relevantEdges = {}
#         for vehicle2 in all_vehicles:
#             # only one comparison per vehicle
#             if vehicle.getID() < vehicle2.getID():
#
#                 intersection_of_two_vehicles = find_intersection(vehicle, vehicle2)
#
#     return (index_route)
#
#
# def find_intersection(vehicle1, vehicle2):
#     # get the polygon of vehicle 1
#     polygon_of_veh1 = vehicle1.get_polygon()
#     new_polygon_of_veh1 = []
#     # convert the polygon to process it for shapely
#     for coordinate in range(0, len(vehicle1.get_polygon())):
#         if coordinate % 2 == 0:
#             point = (polygon_of_veh1[coordinate], polygon_of_veh1[coordinate + 1])
#             new_polygon_of_veh1.append(point)
#
#     # get the polygon of vehicle 2
#     polygon_of_veh2 = vehicle2.get_polygon()
#     new_polygon_of_veh2 = []
#     # convert the polygon to process it for shapely
#     for coordinate in range(0, len(vehicle2.get_polygon())):
#         if coordinate % 2 == 0:
#             point = (polygon_of_veh2[coordinate], polygon_of_veh2[coordinate + 1])
#             new_polygon_of_veh2.append(point)
#
#     # return a list of the points of the intersection
#     return list(Polygon(new_polygon_of_veh1).intersection(Polygon(new_polygon_of_veh2)).exterior.coords)
