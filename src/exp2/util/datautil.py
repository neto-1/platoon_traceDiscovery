import collections
import csv
import os
from typing import Tuple, List

import geopy.distance
import numpy as np
from shapely.geometry import Polygon


class DataUtil:
    @staticmethod
    def convert_coordinates_to_str(coordinates: List[Tuple]) -> str:
        if coordinates[0] != coordinates[-1]:
            raise NameError('Polygon must begin and end with the same coordinate')
        points = ""
        for coordinate in coordinates:
            longitude = coordinate[0]
            latitude = coordinate[1]
            points = points + str(longitude) + ", " + str(latitude)
            if coordinate is not coordinates[-1]:
                points = points + ", "
        points = "[" + points + "]"
        return points

    @staticmethod
    def convert_coordinates_to_flat_list(coordinates: List[Tuple]) -> List:
        if coordinates[0] != coordinates[-1]:
            raise NameError('Polygon must begin and end with the same coordinate')
        points = []
        for coordinate in coordinates:
            longitude = coordinate[0]
            latitude = coordinate[1]

            points.append(longitude)
            points.append(latitude)

        return points

    @staticmethod
    def create_polygon_from_coordinates(coordinates: List) -> Polygon:
        polygon_coords = []
        for i in range(0, len(coordinates)):
            if i % 2 == 0:
                coord = (coordinates[i], coordinates[i + 1])
                polygon_coords.append(coord)
        polygon = Polygon(polygon_coords)

        return polygon

    @staticmethod
    def create_path_from_result_with_vehicle_id(result) -> Tuple:
        vehicle_id = result.get("vehicle_id")
        weight = result.get("weight")
        path = result.get("path")
        shortest_path_distance, shortest_path = DataUtil.create_path_from_path_result(weight, path)
        return vehicle_id, shortest_path_distance, shortest_path

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

    @staticmethod
    def d(point_1: [float, float], point_2: [float, float]):
        '''point_1 = np.asarray(point_1)
        point_2 = np.asarray(point_2)
        return np.linalg.norm(point_1 - point_2)'''
        return geopy.distance.geodesic((point_1[1], point_1[0]), (point_2[1], point_2[0])).meters

    @staticmethod
    def write_iteration(file_name, headers, iteration_dict):
        file_exists = os.path.isfile(file_name)
        with open(file_name, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(iteration_dict)
