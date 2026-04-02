from gurobipy import *
import networkx as nx
from neo4jrestclient.client import GraphDatabase
from columngeneration.model.vehicle import Vehicle
from columngeneration.masterproblem.mpinterface import MPInterface
from columngeneration.subproblem.subproblem import SubProblem
from typing import List


class MasterProblem(MPInterface):

    def __init__(self, savings: float, sub_methods: List[SubProblem]):
        self._savings = savings  # the value of savings
        self._sub_methods = sub_methods  # a list of all submethods to be applied on the mp
        self._vehicles = None  # a list of vehicle objects
        self._db_connection = None  # the connection to database
        self._graph = None  # a nx graph of the road network
        self._mp = None  # Model with binary and integer variables (LP-Model class)
        self._rel_mp = None
        self._variables = None
        self._constraints = None
        self._shadow_prizes = None  # a dict of the shadow variables (edges X vehicles)
        self._obj = float  # a tuple of the objective of mp and relaxed_mp
        self._is_optimal = False

    # run the master problem and solve for the given savings
    def solve_master(self, vehicles: List[Vehicle], db_connection: GraphDatabase) -> None:

        # initiate the object
        self._init_master(vehicles, db_connection)

        # iterate until optimal
        while not self._is_optimal:
            # create the ilp
            self._create_lp()

            # solve the ilp
            self._solve_lp()

            # get shadow prizes
            self._get_shadow_prizes()

            # get new paths
            for sub_problem in self._sub_methods:
                new_path = sub_problem.get_path(self._shadow_prizes, self._vehicles, self._graph)
                self._is_optimal = not new_path

    def _init_master(self, vehicles: List[Vehicle], db_connection: GraphDatabase) -> None:
        self._vehicles = vehicles
        self._db_connection = db_connection
        self._create_graph()

    def _create_graph(self) -> None:
        # query = "MATCH (n1)-[r:NEIGHBOUR]->(n2) RETURN id(n1), id(n2), r.distance, id(r)"
        query = "MATCH (n1)-[r:neighbourEdges]->(n2) where n1.lat < 3 and n1.lat >= 0 and n1.lon > 0 and n1.lon < 9 and n2.lat < 3 and n2.lat >= 0 and n2.lon > 0 and n2.lon < 9 RETURN id(n1), id(n2), r.distance, id(r)"
        # query = "MATCH (n1)-[r:neighbourEdges]->(n2) RETURN id(n1), id(n2), r.distance, id(r)"

        results = self._db_connection.query(query)

        # create the graph for the group
        graph = nx.DiGraph()
        for r in results:
            if r[0] <= r[1]:
                graph.add_edge(r[0], r[1], c=r[2], id=r[3])
            # graph.add_edge(r[1], r[0], c=r[2], id=r[3]+0.5)
        # save the graph
        self._graph = graph

    # create the ilp with the given graph and the given vehicles
    def _create_lp(self) -> None:

        # create the master problem
        master_problem = Model("Master_problem")
        master_problem.setParam("OutputFlag", False)

        # initializing dicts of variables
        x = {}  # vehicle uses a path
        y = {}  # edge is being used by vehicle h at a certain time, this is called "timestamp"
        p = {}  # vehicle h and g are driving at the same time over edge e
        time_helper = {}  # the time vehicle h drives over edge e

        # initiate "big M"-value
        big_m = len(self._vehicles) * quicksum(self._graph[e[0]][e[1]]['c'] for e in self._graph.edges())

        # this adds paths for the vehicles, so that there can be paths chosen in the mp
        for vehiclons in self._vehicles:
            vehiclons.add_relevant_paths_pl()

        # objective for the path variable x
        for veh in self._vehicles:
            x[veh.get_id()] = {}
            # create a binary variable for every tour of a vehicle
            for tour_number in veh.get_all_paths():
                x[veh.get_id()][tour_number.get_route_id()] = master_problem.addVar(vtype=GRB.BINARY, lb=0, obj=round((1 - self._savings) * sum(tour_number.get_distance()), 4),
                                                                                    name="x_" + str(veh.get_id()) + "_" + str(tour_number.get_route_id()))

        # objective for the "timestamp", also initiate time_helper and platoon variable
        for e in self._graph.edges():
            y[e] = {}
            p[e] = {}
            time_helper[e] = {}
            for h in self._vehicles:
                y[e][h.get_id()] = master_problem.addVar(vtype=GRB.BINARY, lb=0, obj=round(self._savings * self._graph[e[0]][e[1]]['c'], 4), name="y_" + str(e) + "_" + str(h.get_id()))
                time_helper[e][h.get_id()] = master_problem.addVar(vtype=GRB.INTEGER, obj=0, name="time_helper_" + str(e) + "_" + str(h.get_id()))
                p[e][h.get_id()] = {}
                for g in self._vehicles:
                    if h.get_id() != g.get_id():
                        p[e][h.get_id()][g.get_id()] = master_problem.addVar(vtype=GRB.BINARY, lb=0, obj=0, name="platoon_" + str(e) + "_" + str(h.get_id()) + "_" + str(g.get_id()))

        # add the variables to the problem
        master_problem.update()

        # !!!!!!!!!! CONSTRAINTS !!!!!!!!!!
        all_constraints = {}
        path_of = {}
        timestamp = {}
        timestamp_min = {}
        time_assign = {}
        time_increase = {}
        same_time = {}

        for veh in self._vehicles:
            timestamp[veh.get_id()] = {}
            timestamp_min[veh.get_id()] = {}
            time_assign[veh.get_id()] = {}
            time_increase[veh.get_id()] = {}
            same_time[veh.get_id()] = {}
            # only one tour per vehicle
            path_of[veh.get_id()] = master_problem.addConstr(quicksum(x[veh.get_id()][tour_number.get_route_id()] for tour_number in veh.get_all_paths()) == 1, name=str("path_of_") + str(veh.get_id()))

            for e in self._graph.edges():
                same_time[veh.get_id()][e] = {}
                # just "buy" a new timestamp, if there is no suitable timestamp in use, in which the actual vehicle cannot join
                timestamp[veh.get_id()][e] = master_problem.addConstr(quicksum(x[veh.get_id()][tour_number.get_route_id()] for tour_number in veh.get_all_paths() if e in tour_number.get_edges()) <= y[e][veh.get_id()]
                                                                      + quicksum(p[e][veh.get_id()][g.get_id()] for g in self._vehicles if g.get_id() < veh.get_id()), name="timestamp_" + str(e) + "_" + str(veh.get_id()))

                # make sure, that the sum of all y values is at least 1, if  a vehicle drives over the edge
                # timestamp_min[veh.get_id()][e] = master_problem.addConstr(quicksum(y[e][vehicle.get_id()] for vehicle in self._vehicles) >=
                #                                                           quicksum(x[veh.get_id()][tour_number.get_route_id()] for tour_number in veh.get_all_paths()
                #                                                                    if e in tour_number.get_edges()), name="timestampMin_" + str(e) + "_" + str(veh.get_id()))

                timestamp_min[veh.get_id()][e] = master_problem.addConstr(quicksum(y[e][vehicle.get_id()] for vehicle in self._vehicles) >=
                                                                          quicksum(p[e][veh.get_id()][veh2.get_id()] for veh2 in self._vehicles if veh2.get_id() != veh.get_id()), name="timestampmin_" + str(e) + "_" + str(veh.get_id()))

                # the condition to set the time variables (time_helper) to a minimum dependent on the reachability from the starting point
                for tour_of_veh in veh.get_all_paths():
                    if e in tour_of_veh.get_edges():

                        # the minimum time to travel an edge "e" in a tour "tour_of_veh" from vehicle "veh"
                        time_assign[veh.get_id()][e] = master_problem.addConstr(sum(tour_of_veh.get_distance()[0:tour_of_veh.get_edges().index(e)+1]) <= time_helper[e][veh.get_id()],
                                                                                name="time_assign_" + str(e) + "_" + str(veh.get_id()) + "_" + str(tour_of_veh.get_route_id()))

                        # make sure, that the times assigned to the edges are increasing
                        for edge2 in tour_of_veh.get_edges():
                            if e[1] == edge2[0]:
                                time_increase[veh.get_id()][e[1]] = master_problem.addConstr(time_helper[edge2][veh.get_id()] - time_helper[e][veh.get_id()] >= self._graph[e[0]][e[1]]['c'],
                                                                                             name="time_increase_" + str(e) + "_" + str(veh.get_id()) + "_" + str(tour_of_veh.get_route_id()))

                # these two constraints make sure, that p is ONLY set to 1, if the times of the vehicles for that edge are the same

                for veh2 in self._vehicles:
                    same_time[veh.get_id()][e][veh2.get_id()] = {}
                    same_time[veh.get_id()][e][veh2.get_id()] = {}
                    if veh2.get_id() < veh.get_id():
                        same_time[veh.get_id()][e][veh2.get_id()]["A"] = master_problem.addConstr(big_m * (1 - p[e][veh.get_id()][veh2.get_id()]) >= time_helper[e][veh.get_id()] - time_helper[e][veh2.get_id()],
                                                                                                  name="same_time_A_" + str(e) + "_" + str(veh.get_id()) + "_" + str(veh2.get_id()))
                        same_time[veh.get_id()][e][veh2.get_id()]["B"] = master_problem.addConstr(big_m * (1 - p[e][veh.get_id()][veh2.get_id()]) >= time_helper[e][veh2.get_id()] - time_helper[e][veh.get_id()],
                                                                                                  name="same_time_B_" + str(e) + "_" + str(veh.get_id()) + "_" + str(veh2.get_id()))

        # store the model to the object itself
        self._mp = master_problem
        self._mp.optimize()

        for e in self._graph.edges():
            for veh in self._vehicles:
                for veh2 in self._vehicles:
                    if veh.get_id() > veh.get_id():
                        if p[e][veh][veh2].X != 0:
                            print(p[e][veh][veh2].X)

        # add the relaxed model
        self._rel_mp = master_problem.relax()
        self._rel_mp.optimize()

        # store also the dictionaries to get the values of shadow prizes and variables later
        self._variables = [x, y, p, time_helper]
        self._constraints = [path_of, timestamp, timestamp_min, time_assign, time_increase, same_time]

        # print("constraints: " + str(self._constraints))

    # solve the master problem and return the output of shadow prizes
    def _solve_lp(self) -> None:
        # solve the Model attached to the object

        self._mp.optimize()

    # method to get the shadow prices
    def _get_shadow_prizes(self) -> None:
        # save the shadow prices of constraints in a dict
        vehicle_shadow_prices = {}
       # self.output_everything()
        for veh in self._vehicles:

            # make a dict to store the shadow prizes
            vehicle_shadow_prices[veh.get_id()] = {}

            # iterate through all constraints and get the shadow prizes != 0
            for constraint in self._rel_mp.getConstrs():
                if constraint.Pi != 0:

                    for e in self._graph.edges():

                        if str(constraint.ConstrName.split('_', -1)[1]) == str(e):
                            vehicle_shadow_prices[veh.get_id()][e] = constraint.Pi

        # save the shadow prizes to the master problem
        self._shadow_prizes = vehicle_shadow_prices

    def output_everything(self):
        print("--------------------------------- output start ----------------------------------------------------")
        shadow_0 = 0
        shadow_18 = 0
        for var in self._mp.getVars():
            if var.X != 0 and str(var.VarName.split('_', -1)[1]) != "helper":
                print(var)
        print("---------------------------------------------------------------------------------------------------")

        for constraint in self._rel_mp.getConstrs():

            if constraint.Pi != 0:
                # print(str(constraint) + " with the value of " + str(constraint.Pi))
                print(str(constraint) + "    " + str(constraint.Pi))
                if str(constraint.ConstrName.split('_', -1)[2]) == "0":
                    shadow_0 += constraint.Pi
                if str(constraint.ConstrName.split('_', -1)[2]) == "18":
                    shadow_18 += constraint.Pi

        print(" test for 0 " + str(shadow_0))
        print(" test for 18 " + str(shadow_18))
        print(self._mp.ObjVal)
        print("--------------------------------- output ending ----------------------------------------------------")

    def show_paths(self):
        for vehicle in self._vehicles:
            for tour in vehicle.get_all_paths():
                print(tour.get_edge_ids())
