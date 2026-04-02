from neo4jrestclient.client import GraphDatabase
import numpy as np
import random
import DBOperations


class PartitioningTestData(object):
    def __init__(self, db):
        self.db = db

    def create_vehicle(self, num_of_vehicles):

        print("by_location")
        start_nodes_id = []
        end_nodes_id = []
        distances = []
        paths_nodes = []

        vehicles = [(94, 257)]
        #vehicles = [(2358, 1159), (2381, 662), (1478, 768)]

        for vehicle in vehicles:
            node1 = vehicle[0]
            node2 = vehicle[1]
            query = "call proceduretest.aStarPlugin(" + str(node1) + ", " + str(node2) + \
                    ", 'distance', 'lat', 'lon', 'coordinates', ['NEIGHBOUR'], [], [], 'both') " \
                    "yield path  WITH  path, extract(n IN relationships(path) | id(n)) as idn, " \
                    "extract(r IN relationships(path) | r.distance) as distance, " \
                    "extract(m IN nodes(path) | id(m)) as idm return idn, distance, idm"
            path = self.db.query(query)
            weights = path.elements[0][1]
            distance = np.sum(weights)
            if distance is not None:
                print node1, node2, distance
                start_nodes_id.append(node1)
                end_nodes_id.append(node2)
                distances.append(round(float(distance), 3))
                paths_nodes.append(path[0][2])

        DBOperations.RunQueries(self.db, start_nodes_id, end_nodes_id, distances,
                                paths_nodes, len(vehicles), "by_location")
