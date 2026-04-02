from neo4jrestclient import client
from pandas import *
from IM import IM

class DB:
    db = client.GraphDatabase("http://localhost:7474", username="neo4j", password="12345678")

    @staticmethod
    def get_incentives(params):
        query = "MATCH (v1:Vehicle)<-[:PAIR]-(p:PlatooningUtility)-[:PAIR]->(v2:Vehicle) " \
                "RETURN v1, v2, (p.vector_degree + p.gradient + p.overlapVol + p.overlapArea) * 0.25 ORDER BY id(v1) "

        results = DB.db.query(query, returns=(client.Node, client.Node))
        return results

    @staticmethod
    def get_vehicles():
        query = "MATCH (v1:Vehicle)<-[:PAIR]-(p:PlatooningUtility)-[:PAIR]->(v2:Vehicle) " \
                "RETURN collect(distinct id(v1))"
        results = DB.db.query(query)
        return results[0][0]

    @staticmethod
    def get_incentive_matrix(params):
        vehicles = DB.get_vehicles()
        incentives = DB.get_incentives(params)

        matrix = [[0 for i in range(len(vehicles))] for i in range(len(vehicles))]

        for i in range(len(incentives)):
            v1 = incentives[i][0]
            ic = incentives[i][2]
            v2 = incentives[i][1]
            matrix[vehicles.index(v1.id)][vehicles.index(v2.id)] = ic

        i_m = IM(matrix)

        return i_m

    # input: a set of tuples (tuples with len <2 will be ignored; types other than tuple will also be ignored)
    # return: nothing
    # function: creates a node "Group" with connection "INGROUP" from every member of the group
    @staticmethod
    def store_groups(groups):
        # get a list of all vehicle ids in the right order (the function "get_vehicles()" should have the right order
        veh_id_list = DB.get_vehicles()

        # filter for group size smaller than 2 and faults in the set of groups
        for group in groups:
            if type(group) == tuple and len(group) > 1:
                query = "Create (g:Group) with g match (v:Vehicle) where id(v) = 0 "
                for veh in group:
                    query = query + str(" or id(v) = ") + str(veh_id_list[veh])
                query = query + " create (g)<-[:INGROUP]-(v)"
                DB.db.query(query)
                print(query)
