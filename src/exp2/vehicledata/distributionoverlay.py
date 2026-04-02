import collections
from typing import Tuple

import numpy as np

from model.vehicleset import VehicleSet
from util.cmd import CMD
from util.databasecontainer import DatabaseContainer
from util.datautil import DataUtil
from vehicledata.database import Database
from vehicledata.vehiclesetcreator import VehicleSetCreator


class DistributionOverlay(VehicleSetCreator):
    overlay_percentage = 3

    def __init__(self, number_of_vehicles: int, set_type: str, max_overlay: float):
        self.number_of_vehicles = number_of_vehicles
        self.set_type = set_type

    def create(self) -> VehicleSet:

        # create a vehicle set, on which we want to prune "false" vehicles in terms of spontaneous platooning
        vehicle_set_id = Database.create_random_vehicle_set(self.number_of_vehicles)
        vehicle_set = VehicleSet(vehicle_set_id, self.set_type,
                                 "gen_overlay_" + str(DistributionOverlay.overlay_percentage))

        # in the beginning, we assume, that there is a path with spontaneous platooning more than "threshold"
        too_much_spontaneous_platooning = True
        # this parameter specifies how much percent of a path can have spontaneous platooning (in percent)
        threshold = DistributionOverlay.overlay_percentage

        # initiate the edge_dict and store the shortest path of vehicles and information, which edge are traversed and how often
        edge_dict = self.get_edge_dict(vehicle_set_id)

        # iterate through the vehicles, until all vehicles satisfy the threshold
        while too_much_spontaneous_platooning:

            # fill the edge_dict, with the information about spontaneous platooning
            edge_dict = self.get_spontaneous_platooning_informations(edge_dict)

            # initiate the max overlap to be zero for vehicle "0"
            max_overlap = (0, 0)
            for veh in edge_dict:
                if veh == "edges":
                    continue
                # if the overlap of this vehicle is more than the actual, we set this as new max_overlap
                if edge_dict[veh]["spontaneous_platoon"][0] > max_overlap[0]:
                    max_overlap = (edge_dict[veh]["spontaneous_platoon"][0], veh)

            # if there is a path with to much spontaneous platooning, we want to delete it
            if max_overlap[0] > threshold:
                # we have to check all records in edge_dict and adjust the edges of the path of the considered vehicle
                for edge in edge_dict[max_overlap[1]]["edges"]:
                    # we want to delete the vehicle, therefore we want to reverse the count of edges from its path
                    edge_dict["edges"][edge] -= 1
                print("delete vehicle:", max_overlap[1])
                # finally delete the vehicle from edge_dict
                del edge_dict[max_overlap[1]]
            # if we cant find another vehicle with to much spontaneous platooning, we set the variable to False
            else:
                too_much_spontaneous_platooning = False

        # here minus 1, because there is also a dict for edges: len of edge_dict is number of vehicles + the dict of edges
        print("there are still this many vehicles left:", len(edge_dict) - 1)

        custom_nodes_vehicles = []
        for vehicle in edge_dict:
            if vehicle == "edges":
                continue
            custom_nodes_vehicles.append(edge_dict[vehicle]["start_and_end"])
        print(custom_nodes_vehicles)
        return vehicle_set

    # create the edge dictionary from the vehicle information and shortest paths
    @staticmethod
    def get_edge_dict(vehicle_set_id):
        # initiate the edge_dict to store the edge information
        edge_dict = {"edges": {}}
        edge_dict["edges"]["all_edges"] = set()

        with DatabaseContainer.driver.session() as session:
            # query = "MATCH (n:" + CMD.vehicle_set_label + ")-[r:" + CMD.vehicle_in_set_rel + "]->(m:" + CMD.vehicle_label + ") RETURN id(n) as node_id_1 ,id(m) as  node_id_2, r.distance_meter as distance, id(r) as rel_id"
            # get the vehicle id and the id of start and end point
            query = "MATCH (n:VehicleSet)-[r:CONSISTS_OF]->(m:Vehicle)-[:START_AT]-(l:RoadPoint), (m)-[:END_AT]-(f:RoadPoint) WHERE id(n) =" + str(
                vehicle_set_id) + " RETURN id(m) as vehicle, id(l) as start, id(f) as end"
            veh_results = session.run(query)

            # iterate through the vehicles to find paths with much overlay
            for veh in veh_results:

                # initiate the lists for the edges and distances
                edge_dict[veh[0]] = {}
                edge_dict[veh[0]]["distance"] = []
                edge_dict[veh[0]]["edges"] = []
                edge_dict[veh[0]]["start_and_end"] = [veh[1], veh[2]]

                # get the shortest path of the vehicle with a star
                query = "MATCH (end:" + CMD.road_label + ")<-[r2:" + CMD.vehicle_end_rel + "]-(v:" + CMD.vehicle_label + ")-[r1:" + CMD.vehicle_start_rel + "]->(start:" + CMD.road_label + ") WHERE id(v)=" + \
                        str(veh[
                                0]) + " with start, end CALL apoc.algo.aStar(start, end, '" + CMD.road_rel + ">', 'distance_meter','lat','lon')  YIELD weight, path RETURN weight, path"
                results = session.run(query)
                result = results.single()

                # extract weight and path from the resulted weight and path
                weight = result.get("weight")
                path = result.get("path")
                # format it to be just the weight and the path information
                (weight, path) = DataUtil.create_path_from_path_result(weight, path)

                # this part prepares the check for the right arc direction
                count = 0
                for relation_id, relation in path.items():
                    if count == 0:
                        end_node = relation['start_node_id'].id
                    count += 1
                # create empty list to create a route for the vehicle
                path_relation_ids = []
                path_relation_distance = []
                list_of_edges = []

                # iterate through all edges to count them
                for relation_id, relation in path.items():

                    # here is the actual check for the direction of an arc: the next arc should have the same starting node as the ending node of the last arc
                    if relation['start_node_id'].id != end_node:
                        raise AttributeError(
                            "Error: The inserted arc has the wrong direction or is not adjacent to the last one")
                    end_node = relation['end_node_id'].id

                    # append the id of the relation to the list
                    path_relation_ids.append(relation_id)

                    # create a list of the distances
                    path_relation_distance.append(relation['distance_meter'])

                    # create a list of edges as a tuple
                    edge = (relation['start_node_id'].id, relation['end_node_id'].id)
                    list_of_edges.append(edge)
                    # if the edge is already stored, we increase the number of that edge by 1
                    if edge in edge_dict["edges"]["all_edges"]:
                        edge_dict["edges"][edge] += 1
                    # if the edge is not stored, we create the dict and add the edge to the set of all edges after
                    if edge not in edge_dict["edges"]["all_edges"]:
                        edge_dict["edges"][edge] = 1
                        edge_dict["edges"]["all_edges"].add(edge)

                # fill the missing values into the dict of vehicle_list
                edge_dict[veh[0]]["distance"] = path_relation_distance
                edge_dict[veh[0]]["edges"] = list_of_edges
        return edge_dict

    # get the percentage and total values of spontaneous platooning
    @staticmethod
    def get_spontaneous_platooning_informations(edge_dict):

        for veh in edge_dict:
            if veh == "edges":
                continue
            # initiate the dict part for the vehicle
            edge_dict[veh]["spontaneous_platoon"] = {}
            # reset the weighted counters for single and platoon
            single = 0
            platoon = 0
            individual_veh_savings = 0
            # make an empty list, for all platooned edges
            spontaneous_platoon_edges = []
            for e in edge_dict[veh]["edges"]:
                # get the number of times, the edge occurred in the starting setup of all vehicles
                edge_occurrence = edge_dict["edges"][e]

                # the next 2 if clauses determine, if the weight of the edge get counted to single(path) or platoon(path) with single + platoon = shortest path distance
                if edge_occurrence == 1:
                    position_of_edge = edge_dict[veh]["edges"].index(e)
                    single += edge_dict[veh]["distance"][position_of_edge]

                if edge_occurrence > 1:
                    position_of_edge = edge_dict[veh]["edges"].index(e)
                    platoon += edge_dict[veh]["distance"][position_of_edge]
                    spontaneous_platoon_edges.append(e)
                    weight_of_edge = edge_dict[veh]["distance"][edge_dict[veh]["edges"].index(e)]
                    individual_veh_savings += ((edge_occurrence - 1) * 0.1 * weight_of_edge) / edge_occurrence

            percentage_spontaneous_platooning = 100 * platoon / (single + platoon)
            # store the information about spontaneous platooning to the edge dictionary
            edge_dict[veh]["spontaneous_platoon"] = (
            percentage_spontaneous_platooning, individual_veh_savings, spontaneous_platoon_edges)
        # return the edge dictionary
        return edge_dict

    # helping method to unwind the attributes
    @staticmethod
    def create_path_from_path_result(weight, path) -> Tuple:
        accumulated_distance = 0
        accumulated_distance_meter = 0
        relationships = collections.OrderedDict()

        for relationship in path:
            accumulated_distance = accumulated_distance + relationship.get("distance")
            accumulated_distance_meter = accumulated_distance_meter + relationship.get("distance_meter")

            start_node_coordinates = np.asarray((relationship.nodes[0].get("lon"), relationship.nodes[0].get("lat")))
            end_node_coordinates = np.asarray((relationship.nodes[1].get("lon"), relationship.nodes[1].get("lat")))

            start_node_id = relationship.nodes[0]
            end_node_id = relationship.nodes[1]

            relationships[relationship.id] = {"distance": relationship.get("distance"),
                                              "accumulated_distance": accumulated_distance,
                                              "start_node_coordinates": start_node_coordinates,
                                              "end_node_coordinates": end_node_coordinates,
                                              "start_node_id": start_node_id, "end_node_id": end_node_id,
                                              "accumulated_distance_meter": accumulated_distance_meter,
                                              "distance_meter": relationship.get("distance_meter")}
        return weight, relationships
