from util.databasecontainer import DatabaseContainer
from util.cmd import CMD
from typing import Dict
import networkx as nx


class Database:
    def __init__(self):
        raise NotImplementedError("static")


    @staticmethod
    def get_road_network() -> nx.DiGraph:
        with DatabaseContainer.driver.session() as session:
            query = "MATCH (n:" + CMD.road_label + ")-[r:" + CMD.road_rel + "]->(m:" + CMD.road_label + ") RETURN id(n) as node_id_1 ,id(m) as  node_id_2, r.distance_meter as distance, id(r) as rel_id"
            results = session.run(query)
            print(query)
            road_network = nx.DiGraph()
            for result in results:
                node_id_1, node_id_2, distance, rel_id = result
                road_network.add_edge(node_id_1, node_id_2, key = rel_id, weight = distance, attr_dict = {'id': rel_id })
                road_network.add_edge(node_id_2, node_id_1, key = rel_id, weight = distance, attr_dict = {'id': rel_id })
            return road_network

    @staticmethod
    def get_groups_vehicles(vehicle_set_id: int) -> Dict:
        with DatabaseContainer.driver.session() as session:
            query = "MATCH (vs:" + CMD.vehicle_set_label + ")-[:" + CMD.vehicle_in_set_rel + "]->(v:" + CMD.vehicle_label + ")-[:IN]->(g:" + CMD.group_label + "), (end)-[:" + CMD.vehicle_end_rel + "]-(v)-[:" + CMD.vehicle_start_rel + "]-(start) WHERE id(vs) = " + str(vehicle_set_id) + " RETURN collect(id(v)) as vehicle_ids , collect(id(start)) as start_node_ids,  collect(id(end)) as end_node_ids, id(g) as group_ids, g.shortest_path_distance as group_distance"
            results = session.run(query)
            groups = {}

            for result in results:
                vehicle_ids, start_node_ids, end_node_ids, group_id, group_distance = result

                group_vehicles = {}
                for i in range(len(vehicle_ids)):
                    group_vehicles[vehicle_ids[i]] = (start_node_ids[i], end_node_ids[i])
                groups[group_id] = (group_vehicles, group_distance)
            return groups


    @staticmethod
    def store_groups_routes(groups):
        with DatabaseContainer.driver.session() as session:
            for group_id, group in groups.items():
                objective_value, vehicles = group
                print("group_id", group_id, "objective_value", objective_value)

                query = "MATCH (group:" + CMD.group_label + ") WHERE ID(group) = " + str(group_id) + " SET group.objective = " + str(objective_value)

                for vehicle_id, vehicle_edges in vehicles.items():
                    print("vehicle_id", vehicle_id, "vehicle_edges", vehicle_edges)

                    start_id = vehicle_edges[0][0]
                    end_id = vehicle_edges[-1][1]

                    query = "MATCH (start:"+ CMD.road_label +") WHERE ID(start) = " + str(start_id) + \
                            " MATCH (end:"+ CMD.road_label +") WHERE ID(end) = " + str(end_id) + \
                            " MATCH (group:"+ CMD.group_label +") WHERE ID(group) = " + str(group_id) + \
                            " MATCH (vehicle:"+ CMD.vehicle_label +") WHERE ID(vehicle) = "  + str(vehicle_id) + \
                            " CREATE (vehicle)-[:"+ CMD.platoon_at_rel +"]->(platoonRoute:"+ CMD.platoon_route_label +")-[:"+ CMD.in_group_rel +"]->(group)" \
                            " CREATE(platoonRoute)-[:"+ CMD.start_at_rel +"]->(platoonRouteNode:" + CMD.platoon_route_node_label + ")" \
                            " CREATE(platoonRoute)-[:"+ CMD.route_nodes_rel +"]->(:"+ CMD.platoon_via_label +")-[:" + CMD.platoon_via_rel + "]->(platoonRouteNode)" \
                            " MERGE(location: "+ CMD.location_label +")-[:" + CMD.location_rel + "]->(start) " \
                            " CREATE (platoonRouteNode)-[:"+ CMD.location_at_rel +"]->(location)" \
                            " WITH group, end, platoonRoute, platoonRouteNode as startRouteNode" \
                            " CREATE (platoonRoute)-[:"+ CMD.end_at_rel +"]->(platoonRouteNode:" + CMD.platoon_route_node_label + ")" \
                            " CREATE (platoonRoute)-[:"+ CMD.route_nodes_rel +"]->(:"+ CMD.platoon_via_label +")-[:" + CMD.platoon_via_rel + "]->(platoonRouteNode)" \
                            " MERGE (location:"+ CMD.location_label +")-[:" + CMD.location_rel + "]->(end)" \
                            " CREATE (platoonRouteNode)-[:" + CMD.location_at_rel + "]->(location)" \
                            " RETURN ID(platoonRoute) AS platoonRouteId, ID(startRouteNode) AS startRouteNodeId, ID(platoonRouteNode) AS endRouteNodeId"

                    print(query)

                    # ToDo edges distance from ilp

                    for vehicle_edge in vehicle_edges:
                        # print(vehicle_edge)

                        query = """
                        """

Database.get_road_network()

print("jau")