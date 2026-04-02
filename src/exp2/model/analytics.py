from typing import Dict, Tuple, List

from gurobipy import *

from util.configuration import Configuration
from util.databag import DataBag


class Analytics:
    def __init__(self):
        raise NotImplementedError("static")

    @staticmethod
    def calculate_platooning_shortest_path_routes(saving_factor: float, vehicle_paths: List[Tuple]):

        # edges = [(v_id, e_id, distance)]
        edges = []
        for vehicle_path in vehicle_paths:
            vehicle_id = vehicle_path[0]
            vehicle_edges = vehicle_path[2]
            for vehicle_edge_id in vehicle_edges:
                edges.append((vehicle_id, vehicle_edge_id, vehicle_edges[vehicle_edge_id]["distance_meter"]))

        distances = {}
        y = {}
        x = {}
        for edge in edges:
            e_id = edge[1]
            distances[e_id] = edge[2]
            y[e_id] = 1
            if e_id not in x:
                x[e_id] = 1
            else:
                x[e_id] += 1

        # for e_id, distance in distances.items():
        #     print(e_id, distance)
        #     # print(y[e_id])

        sum_distances = sum((saving_factor * y[e_id] + (1 - saving_factor) * x[e_id]) * distance for e_id, distance in
                            distances.items())

        # print(saving_factor, 1 - saving_factor)
        # print(sum_distances)

        return sum_distances

    @staticmethod
    def calculate_path_distance_after_saving(saving_factor: float, vehicle_list):
        """
        # edges = [(v_id, e_id, distance)]
        #vehicles = DataBag.get('tc.vehicles')

        calculate spontaneous platooning distance for all companies
        """
        edges = []

        for key in vehicle_list.keys():
            vehicle_id = key
            vehicle_edges = vehicle_list[key][1][3]
            for edge in range(len(vehicle_edges)):
                edges.append((vehicle_id, vehicle_edges[edge], vehicle_list[key][1][1][edge]))

        distances = {}
        y = {}
        x = {}
        for edge in edges:
            e_id = edge[1]
            distances[e_id] = edge[2]
            y[e_id] = 1
            if e_id not in x:
                x[e_id] = 1
            else:
                x[e_id] += 1

        # for e_id, distance in distances.items():
        #     print(e_id, distance)
        #     # print(y[e_id])

        sum_distances = sum((saving_factor * y[e_id] + (1 - saving_factor) * x[e_id]) * distance for e_id, distance in
                            distances.items())

        # print(saving_factor, 1 - saving_factor)
        # print(sum_distances)

        return sum_distances

    @staticmethod
    def calculate_platooning_shortest_path_routes_ilp(saving_factor: float, vehicle_paths: List[Tuple]) -> Tuple[
        float, Dict[int, List[Tuple[int, int, float, int]]]]:
        """
        :param saving_factor
        :param vehicle_paths:
        :return:
        """
        # ToDo validate new spatial.intersects functions

        road_network = Database.get_road_network()
        # road_network = Database.get_road_network_by_group_id(group_id)

        model = Model("ShortestPathRouting")
        model.setParam("OutputFlag", Configuration.grb_output_flag)
        model.setParam("NodefileStart", Configuration.grb_node_file_start)
        model.setParam("Threads", Configuration.grb_threads)

        x = {}
        y = {}

        """ Objective Function """
        for edge in road_network.edges():
            x[edge] = {}
            y[edge] = model.addVar(vtype=GRB.BINARY, obj=saving_factor * road_network.get_edge_data(*edge)["weight"])

            for vehicle_path in vehicle_paths:
                vehicle_id = vehicle_path[0]
                vehicle_edges = vehicle_path[2]

                start = vehicle_edges[list(vehicle_edges.keys())[0]]
                end = vehicle_edges[list(vehicle_edges.keys())[-1]]
                start_node = start.get("start_node_id")
                end_node = end.get("end_node_id")

                h = vehicle_id

                x[edge][h] = model.addVar(vtype=GRB.BINARY, lb=0,
                                          obj=(1 - saving_factor) * road_network.get_edge_data(*edge)["weight"])

        model.update()

        """ Flow Conservation Constraints """
        for v in road_network.nodes():

            for vehicle_path in vehicle_paths:
                vehicle_id = vehicle_path[0]
                vehicle_edges = vehicle_path[2]

                start = vehicle_edges[list(vehicle_edges.keys())[0]]
                end = vehicle_edges[list(vehicle_edges.keys())[-1]]
                start_node = start.get("start_node_id")
                end_node = end.get("end_node_id")

                h = vehicle_id
                locations = (start_node.id, end_node.id)

                if locations[0] == v:
                    b = 1
                elif locations[1] == v:
                    b = -1
                else:
                    b = 0
                model.addConstr(quicksum(x[edge][h] for edge in road_network.out_edges(v)) - quicksum
                (x[edge][h] for edge in road_network.in_edges(v)) == b)

        """ Edge Using Constraints """
        for edge in road_network.edges():
            for vehicle_path in vehicle_paths:
                vehicle_id = vehicle_path[0]
                h = vehicle_id

                model.addConstr(x[edge][h] <= y[edge])

        """ Shortest Path Constraints """
        for vehicle_path in vehicle_paths:
            vehicle_id = vehicle_path[0]
            vehicle_edges = vehicle_path[2]
            h = vehicle_id
            for vehicle_edge_id in vehicle_edges:
                vehicle_edge = (vehicle_edges[vehicle_edge_id].get("start_node_id").id,
                                vehicle_edges[vehicle_edge_id].get("end_node_id").id)
                model.addConstr(x[vehicle_edge][h] >= 1)

        model.optimize()

        """ Model was proven to be infeasible """
        if model.status == 3:
            model.computeIIS()
            for c in model.getConstrs():
                if c.IISConstr > 0:
                    print("Infeasible model:", c.ConstrName)

        if model.status == 2:
            vehicles_distance = {}

            vehicles_routes = {}
            # vehicle = {}
            for vehicle_path in vehicle_paths:
                vehicle_id = vehicle_path[0]
                vehicle_edges = vehicle_path[2]

                start = vehicle_edges[list(vehicle_edges.keys())[0]]
                end = vehicle_edges[list(vehicle_edges.keys())[-1]]
                start_node = start.get("start_node_id")
                end_node = end.get("end_node_id")

                h = vehicle_id
                locations = (start_node.id, end_node.id)

                vehicles_distance[h] = 0
                # vehicle[h] = []

                vehicle_route_edges = {}

                for edge in road_network.edges():
                    if x[edge][h].X > 0.99:
                        vehicles_distance[h] = road_network.get_edge_data(*edge)["weight"] + vehicles_distance[h]
                        # Hash
                        vehicle_route_edges[edge[0]] = (edge[0], edge[1], road_network.get_edge_data(*edge)["weight"],
                                                        road_network.get_edge_data(*edge)["attr_dict"]["id"])

                # Sort edges to get vehicle route
                vehicle_route = [vehicle_route_edges[locations[0]]]
                for i in range(len(vehicle_route_edges) - 1):
                    vehicle_route.append(vehicle_route_edges[vehicle_route[len(vehicle_route) - 1][1]])

                """ vehicle_route list of start node id, end node id, distance_meter and relationship id  """
                vehicles_routes[h] = vehicle_route

            return model.ObjVal, vehicles_routes

    @staticmethod
    def get_group_global_solution(vehicle_global_path_distance, group_vehicles) -> Dict[int, int]:
        group_global_path_distance = {}
        for group_id, group in group_vehicles.items():
            group_global_path_distance[group_id] = 0
            for vehicle, path_distance in vehicle_global_path_distance:
                if vehicle in group:
                    group_global_path_distance[group_id] += path_distance
        return group_global_path_distance

    @staticmethod
    def calculate_group_global_solution(vehicle_set_id: int, group_vehicles: Dict[int, List[int]]) -> Dict[int, int]:
        """
        calculate the cost of routes in the global solution (cooperative solution) for each company separately
        """
        if not DataBag.has_key('test_cases'):
            return None
        if type(DataBag.get('test_cases')) != list:
            vehicle_global_path_distance = DataBag.get(
                'test_cases.algorithms.disjointness.disjointness.shortest_path_distance')
            return Analytics.get_group_global_solution(vehicle_global_path_distance, group_vehicles)

        for test_case in DataBag.get('test_cases'):
            current_set_id = DataBag.get_from_dict(test_case, 'vehicle_set_id')
            if vehicle_set_id == current_set_id:
                grouping_method = DataBag.get_from_dict(test_case, 'algorithms.grouping.method')
                if grouping_method == "SingleGroup":
                    vehicle_global_path_distance = DataBag.get_from_dict(test_case,
                                                                         'algorithms.disjointness.disjointness.shortest_path_distance')
                    return Analytics.get_group_global_solution(vehicle_global_path_distance, group_vehicles)
