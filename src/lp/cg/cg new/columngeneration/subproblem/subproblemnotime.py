from gurobipy import *
from columngeneration.model.route import Route
from columngeneration.model.vehicle import Vehicle
from neo4jrestclient.client import GraphDatabase
from columngeneration.subproblem.spinterface import SPInterface
from typing import Dict, Tuple, List


class SubProblemNoTime(SPInterface):

    def __init__(self, savings: float):
        self._savings = savings
        self._index = 0
        self._vehicles = None
        self._graph = None
        self._shadow_prizes = None
        self._new_path = 0
        self._model = {}
        self._y = {}
        self._same_path = False

    # initiation method
    def _init_sub(self, shadow_prizes: Dict[Tuple[int, int], float], vehicles: List[Vehicle], graph: GraphDatabase) -> None:
        # store shadow prizes
        self._shadow_prizes = shadow_prizes
        # store the vehicles
        self._vehicles = vehicles
        # store graph information
        self._graph = graph
        # get the actual (maximal) id of the paths
        self._count_existing_paths()

    def _count_existing_paths(self) -> None:
        self._index = 0
        for veh in self._vehicles:
            self._index += len(veh.get_all_paths())

    # get the shadow prizes
    def get_path(self, shadow_prizes: Dict[Tuple[int, int], float], vehicles: List[Vehicle], graph: GraphDatabase) -> int:
        # reset the new-path-variable to 0:
        self._new_path = 0
        # initiate the sub
        self._init_sub(shadow_prizes, vehicles, graph)

        # run the sub and create new paths
        self._sub_problem_dual_lp()

        # get the routes
        self._create_route()

        return self._new_path

    def _sub_problem_dual_lp(self):

        # iterate over all vehicles
        for veh in self._vehicles:

            # start the optimization process
            create_route = Model("create_route")
            create_route.setParam("OutputFlag", False)
            create_route.ModelSense = 1
            y = {}  # binary variable, indicating if edge e is being used

            # only one variable in the objective: the weight of the traveled edges
            for e in self._graph.edges():

                if str(e) in self._shadow_prizes['edge_list']:
                    y[e] = create_route.addVar(vtype=GRB.BINARY, obj=self._graph[e[0]][e[1]]['c'] - sum(self._shadow_prizes[vehicle_id.get_id()].get(e, float(0)) for vehicle_id in self._vehicles) + self._shadow_prizes[veh.get_id()].get(e, float(0)))
                else:
                    y[e] = create_route.addVar(vtype=GRB.BINARY, obj=self._graph[e[0]][e[1]]['c'])
            create_route.update()

            # constraint: it has to be a path from start to end node
            for v in self._graph.nodes():
                if v == veh.get_start():
                    b = 1

                elif v == veh.get_end():
                    b = -1

                else:
                    b = 0
                create_route.addConstr(quicksum(y[e] for e in self._graph.out_edges(v)) - quicksum(y[e] for e in self._graph.in_edges(v)) == b)

            # optimize the lp
            self._model[veh.get_id()] = create_route
            self._y[veh.get_id()] = y
            self._model[veh.get_id()].optimize()

    def _create_route(self):
        # ========== create route as an object =====
        for veh in self._vehicles:

            # the list of the edge Ids
            route = []
            # the list of the distances per edge
            route_distances = []
            # the list of the edges on the path
            route_edges = []
            # variable for decide if the new path is worthy
            atimesu = 0

            self._same_path = False
            # check if the new path would make a better OptVal in the master problem

            for var, value in self._y[veh.get_id()].items():
                if value.X != 0:

                    # create route with IDs of the edges
                    route.append(self._graph[var[0]][var[1]]['id'])

                    # create a list of the distances
                    route_distances.append(self._graph[var[0]][var[1]]['c'])
                    # create a ordered list of the path with every edge displayed as two nodes
                    route_edges.append(var)

                    # calculate a times u for the decision of including the route to the set of routes of the vehicle
                    # for other_veh in self._vehicles:
                    #     if veh.get_id() != other_veh.get_id() and str(var) in self._shadow_prizes['edge_list']:
                    #         atimesu += self._y[var].X * self._shadow_prizes[other_veh.get_id()][str(var) + " " + str(other_veh.get_id())]
                    #         print(str(atimesu) + " waaaaaaaaaaaaaaaaaaaaaas")
            print(" ------start of veh ------------------------------------- vehicle id:  " + str(veh.get_id()))
            # check if the path is already in the set of paths of the vehicle
            set1 = set(route)
            print("new tour: " + str(veh.get_id()) + " -- " + str(set1))
            for tours in veh.get_all_paths():
                set2 = set(tours.get_edge_ids())

                # if the differences in both sets to each other are 0, then its the same path
                if len(set1.difference(set2)) == 0 and len(set2.difference(set1)) == 0:

                    self._same_path = True
                    print("old tour is !! same !!: " + str(veh.get_id()) + " -- " + str(set2))
                else:
                    print("old tour (not same): " + str(veh.get_id()) + " -- " + str(set2))


            print("same path variable: " + str(self._same_path))

            if not self._same_path:
                # print("not same path here")
                # check if the new path has a better solution for the master problem
                reduction_coefficient = sum(route_distances) - (1/0.9)*(atimesu + self._shadow_prizes[veh.get_id()]["path of : " + str(veh.get_id())])
                # print(reduction_coefficient)
                # print("summe")
                # print(route_distances)
                # print(sum(route_distances))
                # print(self._shadow_prizes[veh.get_id()]["path of : " + str(veh.get_id())])
                # print(reduction_coefficient)
                if reduction_coefficient < 0.0000001:
                    # increase route ID
                    self._index += 1
                    # create Route object

                    new_path = Route(self._index, route_distances, route_edges, route)
                    # add the path to the vehicle
                    veh.add_path(new_path)
                    self._new_path += 1
        print("---- all tours: ")
        for vehic in self._vehicles:
            for tour in vehic.get_all_paths():
                print("check tours: " + str(vehic.get_id()) + " -- " + str(tour.get_edges()))
                pass
        print(">>> end iteration !!--")
