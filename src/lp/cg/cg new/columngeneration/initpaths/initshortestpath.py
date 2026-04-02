from columngeneration.model.route import Route
from typing import List
from columngeneration.model.vehicle import Vehicle
from columngeneration.initialsolutioncreator.initpathsinterface import InitPathsInterface
outputControlValues = False


class InitShortestPath(InitPathsInterface):

    def __init__(self) -> None:
        self._vehicles = None
        self._index_routes = None

# do not give the vehicles but get the vehicles when the object is created
    def init_paths(self, vehicles: List[Vehicle]) -> int:
        index_route = 0
        print("iniiiiiiiiiiiiiiit")
        # for vehicle in vehicles:
        #     # new index for next route
        #     index_route += 1
        #
        #     # get the shortest path
        #     query = 'call proceduretest.aStarPlugin(' + str(vehicle.get_start()) + ', ' + str(vehicle.get_end()) \
        #             + ', "distance", "lat", "lon", "coordinates", ["NEIGHBOUR"], [], [], "both") yield path  WITH ' \
        #               ' path, extract(n IN relationships(path) | id(n)) as idn, extract(r IN relationships(path)' \
        #               ' | r.distance) as distance, extract(m IN nodes(path) | id(m)) as idm return idn, distance, idm'
        #     query = 'call proceduretest.aStarPlugin(' + str(vehicle.get_start()) + ', ' + str(vehicle.get_end()) \
        #             + ', "distance", "lat", "lon", "coordinates", ["neighbourEdges"], [], [], "both") yield path  WITH ' \
        #               ' path, extract(n IN relationships(path) | id(n)) as idn, extract(r IN relationships(path)' \
        #               ' | r.distance) as distance, extract(m IN nodes(path) | id(m)) as idm return idn, distance, idm'
        #     res = graph.query(query)
        #     print(query)
        #     # create a list of the edges consisting of tuples of the form:   edge := (node1, node2)
        #     edge_list_of_nodes = list()
        #     for nodes in range(1, len(res[0][2])):
        #         edge_list_of_nodes.append((res[0][2][nodes - 1], res[0][2][nodes]))
        #
        #     # create a route object for every route of the format: (index:int, list of edge ids: int, list of edges: (int, int), list of nodes: int)
        #     shortest_path_of_vehicle = Route(index_route, res[0][1], edge_list_of_nodes, res[0][0])
        #
        #     # add the shortestPath-Route to the routes of the vehicle
        #     vehicle.add_path(shortest_path_of_vehicle)

        return index_route
