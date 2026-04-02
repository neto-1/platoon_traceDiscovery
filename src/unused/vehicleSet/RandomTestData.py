from neo4jrestclient.client import GraphDatabase
import numpy as np
import random
import DBOperations


class RandomData(object):
    def __init__(self, db):
        self.db = db

    def create_vehicle(self, num_of_vehicles):
        query = "match (n:loc) return ID(n)"
        result = self.db.query(query)
        start_nodes_id = []
        end_nodes_id = []
        distances = []
        paths_nodes = []
        count = 0
        while count != num_of_vehicles:
            rand1 = random.randrange(0, len(result)-1)
            rand2 = random.randrange(0, len(result)-1)
            node1 = result[rand1][0]
            node2 = result[rand2][0]
            query = "call proceduretest.aStarPlugin(" + str(node1) + ", " + str(node2) + \
                    ", 'distance', 'lat', 'lon', 'coordinates', ['NEIGHBOUR'], [], [], 'both') " \
                    "yield path  WITH  path, extract(n IN relationships(path) | id(n)) as idn, " \
                    "extract(r IN relationships(path) | r.distance) as distance, " \
                    "extract(m IN nodes(path) | id(m)) as idm return idn, distance, idm"
            path = self.db.query(query)
            weights = path.elements[0][1]
            distance = np.sum(weights)
            if distance is not None:
                # print count, node1, node2, distance
                start_nodes_id.append(node1)
                end_nodes_id.append(node2)
                distances.append(round(float(distance), 3))
                paths_nodes.append(path[0][2])
                count = count+1
        DBOperations.RunQueries(self.db, start_nodes_id, end_nodes_id, distances,
                                paths_nodes, num_of_vehicles, "random")
