from gurobipy import *
import string


def master_problem_lp(vehicles, graph, saving):
    # create the master problem
    master_problem = Model("Masterproblem")
    master_problem.setParam("OutputFlag", False)

    # Assoz. array - dict
    x = {}  # vehicle uses a path
    y = {}  # edge is being used

    # objective for x
    for veh in vehicles:
        x[veh.getID()] = {}
        # create a binary variable for every tour of a vehicle
        for tour_number in veh.getPaths():
            x[veh.getID()][tour_number.getRouteID()] = {}
            x[veh.getID()][tour_number.getRouteID()] = master_problem.addVar(vtype=GRB.BINARY,
                                                                             lb=0,
                                                                             obj=(1 - saving) * sum(tour_number.
                                                                                                    getDistance()))

    # objective for y
    for e in graph.edges():
        y[e] = {}
        # the saving factor is divided by 2, because the edges are iterated 2 times
        # (because for a "normal" edge there are two directed edges)
        # y[e] = m.addVar(vtype=GRB.BINARY, lb=0, obj=(saving) * G[e[0]][e[1]]['c'])
        y[e] = master_problem.addVar(vtype=GRB.BINARY, lb=0, obj=saving * graph[e[0]][e[1]]['c'])

        master_problem.update()

    # constraints
    for veh in vehicles:
        # only one tour per vehicle
        master_problem.addConstr(
            quicksum(x[veh.getID()][tour_number.getRouteID()] for tour_number in veh.getPaths()) >= 1,
            name=str("path of : ") + str(veh.getID()))

    # edge constraints
    edge_constraint = {}
    for e in graph.edges():
        edge_constraint[e] = {}
        for veh in vehicles:
            edge_constraint[e][veh.getID()] = \
                master_problem.addConstr(y[e] >=
                                         quicksum(x[veh.getID()][tour_number.getRouteID()]
                                                  for tour_number in veh.getPaths() if e in
                                                  tour_number.getNodesPath()), name=str(e) + "_" + str(veh.getID()))

    master_problem.optimize()

    # Output and return values
    tour_dictionary = {}

    for veh in vehicles:
        for tour_number in veh.getPaths():
            if x[veh.getID()][tour_number.getRouteID()].X > 0.99:
                tour_dictionary[veh.getID()] = tour_number.getRouteID()
    # "------------------ Output of MasterProblem ends here ------------------"

    # make a relaxed version of the LP to retrieve the dual variables
    relaxed_master_problem = master_problem.relax()
    relaxed_master_problem.optimize()

    # save the shadow prices of constraints in a dict
    vehicle_shadow_prices = {'edge_list': set()}
    # iterate the vehicles
    for veh in vehicles:
        # make a list for the edges for every vehicle
        vehicle_shadow_prices[veh.getID()] = {}
        for c in relaxed_master_problem.getConstrs():
            # if the name of the vehicle is not not in the string name of the constraint
            # add the name and the shadow price to the list for that vehicle
            if string.find(c.ConstrName, str(veh.getID())) > -1:
                # add the edge with value to vehicle_shadow_prices
                if c.pi != 0:
                    edge_name = c.ConstrName.split('_', -1)
                    vehicle_shadow_prices[veh.getID()][edge_name[0]] = c.pi
                    # add the name of the edge to the set
                    vehicle_shadow_prices['edge_list'].add(edge_name[0])
                if string.find(c.ConstrName, "path of") > -1:
                    vehicle_shadow_prices[veh.getID()][c.ConstrName] = c.pi

    return master_problem.ObjVal, tour_dictionary, vehicle_shadow_prices
