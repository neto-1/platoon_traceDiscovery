from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from columngeneration.model.route import Route
from columngeneration.model.vehicle import Vehicle
from columngeneration.subproblem.spinterface import SPInterface
from typing import List, Dict, Tuple


class SubProblem(SPInterface):

    def __init__(self, savings: float):
        self._savings = savings
        self._index = 0
        self._vehicles = None
        self._graph = None
        self._shadow_prizes = None
        self._new_path = False
        self._model = {}
        self._y = {}
        self._same_path = False

    def new_paths(self, shadow_prize: Dict[Tuple[int, int], float]):
        pass

    # get the shadow prizes
    def get_path(self, shadow_prizes: Dict[Tuple[int, int], float], vehicles: List[Vehicle], graph: GraphDatabase) -> bool:

        self._new_path = False

        # initiate the sub
        self._init_sub(shadow_prizes, vehicles, graph)

        # run the sub and create new paths
        self._sub_problem_dual_lp()

        # optimize every model
        self._optimize_model()

        # get the routes
        self._create_route()

        return self._new_path

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

    # run the sub-problem
    def _sub_problem_dual_lp(self) -> None:

        # iterate over all vehicles
        for veh in self._vehicles:

            # start the optimization process with the updated graph
            create_route = Model("create_route")
            create_route.setParam("OutputFlag", False)
            create_route.ModelSense = 1
            y = {}  # binary variable, indicating if edge e is being used

            # only one variable in the objective: the weight of the traveled edges
            for e in self._graph.edges():
                if str(e) in str(self._shadow_prizes[veh.get_id()]):
                    y[e] = create_route.addVar(vtype=GRB.BINARY, obj=self._graph[e[0]][e[1]]['c'] + self._shadow_prizes[veh.get_id()][e], name=str(e))

                else:
                    y[e] = create_route.addVar(vtype=GRB.BINARY, obj=self._graph[e[0]][e[1]]['c'], name=str(e))
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

            # save the model
            create_route.optimize()
            self._model[veh.get_id()] = create_route
            self._y[veh.get_id()] = y

    # optimize the lp
    def _optimize_model(self, vehicle_id: int = -1) -> None:
        if vehicle_id == -1:
            for veh in self._vehicles:
                self._model[veh.get_id()].optimize()
        else:
            self._model[vehicle_id].optimize()

    # create the path from the optimization
    def _create_route(self, vehicle_id: int = -1):
        if vehicle_id == -1:
            for vehicle in self._vehicles:

                # ========== create route as an object =====
                # create empty set of all edges
                route_dict = {}
                for e in self._graph.edges():
                    if self._y[vehicle.get_id()][e].X > 0.9:
                        route_dict[e[0]] = e

                # start the list with the first element
                route = [route_dict[vehicle.get_start()]]

                # for the rest of the edges just append the respectively next edge
                for i in range(len(route_dict)-1):
                    route.append(route_dict[route[len(route)-1][1]])

                route_distances = []
                route_edge_id = []
                # create the other two lists for the route (distances and edge-IDs
                for edge in route:
                    # the list of the distances per edge
                    route_distances.append(self._graph[edge[0]][edge[1]]['c'])
                    # the list of the nodes on the path
                    route_edge_id.append(self._graph[edge[0]][edge[1]]['id'])

                # !!!!!!!!!! check weather the new path can be added !!!!!!!!!!
                # check if the path is already in the set of paths of the vehicle
                set1 = set(route)
                print(route)
                for tours in vehicle.get_all_paths():
                    set2 = set(tours.get_edge_ids())
                    # if the differences in both sets to each other are 0, then its the same path
                    if len(set1.difference(set2)) == 0 and len(set2.difference(set1)) == 0:
                        self._same_path = True

                print(self._same_path)

                if not self._same_path:
                    # check if the new path has a better solution for the master problem

                    # reduction_coefficient = sum(route_distances) - (1/0.9)*(atimesu + self._shadow_prizes[vehicle.get_id()])
                    reduction_coefficient = -1
                    # print(reduction_coefficient)
                    # print(reduction_coefficient)
                    if reduction_coefficient < 0.0000001:
                        # print("new path here")
                        # increase route ID
                        self._index += 1

                        # create Route object
                        new_path = Route(self._index, route_distances, route, route_edge_id)
                        # add the path to the vehicle
                        vehicle.add_path(new_path)
                        # set the variable for the iteration of the main loop to true
                        self._new_path = True

                # add the new paths and count the index
               # self._index += 1
               # vehicle.add_path(Route(self._index, route, route_distances, route_edge_id))
