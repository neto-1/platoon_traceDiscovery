from gurobipy import *
import networkx as nx
from neo4jrestclient.client import GraphDatabase
from columngeneration.masterproblem.mpinterface import MPInterface
from columngeneration.subproblem.subproblem import SubProblem
from columngeneration.subproblem.subproblemnotime import SubProblemNoTime
from columngeneration.model.vehicle import Vehicle
from typing import List


class MasterNoTime(MPInterface):

    # init function
    def __init__(self, savings: float, sub_methods: List[SubProblem or SubProblemNoTime]):
        self._savings = savings  # the value of savings
        self._sub_methods = sub_methods  # a list of all sub methods to be applied on the mp
        self._vehicles = None  # a list of vehicle objects
        self._db_connection = None  # the connection to database
        self._graph = None  # a nx graph of the road network
        self._mp = None  # Model with binary and integer variables (LP-Model class)
        self._rel_mp = None
        self._variables = None
        self._constraints = None
        self._shadow_prizes = None  # a dict of the shadow variables (edges X vehicles)
        self._obj = 0  # a tuple of the objective of mp and relaxed_mp
        self._is_optimal = False

    # the interface
    def solve_master(self, vehicles: List[Vehicle], db_connection: GraphDatabase) -> None:

        # initiate the object
        self._init_master(vehicles, db_connection)

        while not self._is_optimal:
            # create the ilp
            self._create_lp()

            # get shadow prizes
            self._get_shadow_prizes()

            # get new paths
            for sub_problem in self._sub_methods:

                new_path = sub_problem.get_path(self._shadow_prizes, self._vehicles, self._graph)

                if new_path > 0:
                    self._is_optimal = False
                else:
                    self._is_optimal = True

    # initiate master problem
    def _init_master(self, vehicles: List[Vehicle], db_connection: GraphDatabase) -> None:
        self._vehicles = vehicles
        self._db_connection = db_connection
        self._create_graph()

    # create the graph
    def _create_graph(self) -> None:
        # query = "MATCH (n1)-[r:NEIGHBOUR]->(n2) RETURN id(n1), id(n2), r.distance, id(r)"
        query = "MATCH (n1)-[r:neighbourEdges]->(n2) where n1.lat < 3 and n1.lat >= 0 and n1.lon > 0 and n1.lon < 8 RETURN id(n1), id(n2), r.distance, id(r)"
        results = self._db_connection.query(query)

        # create the graph for the group
        graph = nx.DiGraph()
        for r in results:
            graph.add_edge(r[0], r[1], c=r[2], id=r[3])
            graph.add_edge(r[1], r[0], c=r[2], id=r[3]+0.5)
        # save the graph
        self._graph = graph

        # !!!!!!!!!!! ADD a path !!!!!!!!!!!!!!!!
       # # this adds paths for the vehicles, so that there can be paths chosen in the mp
        for vehiclons in self._vehicles:
            vehiclons.add_relevant_paths_pl()

    # create the master problem
    def _create_lp(self) -> None:
        master_problem = Model("Masterproblem")
        master_problem.setParam("OutputFlag", False)

        # Assoz. array - dict
        x = {}  # vehicle uses a path
        y = {}  # edge is being used

        # objective for x
        for veh in self._vehicles:
            x[veh.get_id()] = {}
            # create a binary variable for every tour of a vehicle
            for tour_number in veh.get_all_paths():
                x[veh.get_id()][tour_number.get_route_id()] = {}
                x[veh.get_id()][tour_number.get_route_id()] = master_problem.addVar(vtype=GRB.BINARY, lb=0, obj=(1 - self._savings) * sum(tour_number.get_distance()))

        # objective for y
        for e in self._graph.edges():
            y[e] = master_problem.addVar(vtype=GRB.BINARY, lb=0, obj=self._savings * self._graph[e[0]][e[1]]['c'])

            master_problem.update()

        # constraints
        for veh in self._vehicles:
            # only one tour per vehicle
            master_problem.addConstr(quicksum(x[veh.get_id()][tour_number.get_route_id()] for tour_number in veh.get_all_paths()) >= 1, name=str("path of : ") + str(veh.get_id()))

        # edge constraints
        edge_constraint = {}
        for e in self._graph.edges():
            edge_constraint[e] = {}
            for veh in self._vehicles:
                edge_constraint[e][veh.get_id()] = master_problem.addConstr(y[e] >= quicksum(x[veh.get_id()][tour_number.get_route_id()] for tour_number in veh.get_all_paths()
                                                                                             if e in tour_number.get_edges()), name=str(e) + "_" + str(veh.get_id()))
        self._mp = master_problem
        self._mp.optimize()

    # create the shadow prizes
    def _get_shadow_prizes(self):

        # make a relaxed version of the LP to retrieve the dual variables
        self._rel_mp = self._mp.relax()
        self._rel_mp.optimize()

        # save the shadow prices of constraints in a dict
        vehicle_shadow_prices = {'edge_list': set()}
        # iterate the vehicles
        for veh in self._vehicles:
            # make a list for the edges for every vehicle
            vehicle_shadow_prices[veh.get_id()] = {}
            for c in self._rel_mp.getConstrs():
                # if the name of the vehicle is not not in the string name of the constraint
                # add the name and the shadow price to the list for that vehicle
                if str.find(c.ConstrName, str(veh.get_id())) > -1:
                    # add the edge with value to vehicle_shadow_prices
                    if c.pi != 0:
                        edge_name = c.ConstrName.split('_', -1)
                        for e in self._graph.edges():
                            if edge_name[0] == str(e):
                                vehicle_shadow_prices[veh.get_id()][e] = c.pi
                                # add the name of the edge to the set
                                vehicle_shadow_prices['edge_list'].add(edge_name[0])
                            if str.find(c.ConstrName, "path") > -1:
                                vehicle_shadow_prices[veh.get_id()][c.ConstrName] = c.pi
        # save the shadow prices
        self._shadow_prizes = vehicle_shadow_prices
