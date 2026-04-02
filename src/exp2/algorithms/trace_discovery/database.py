import datetime
import time
import logging
# from math import comb
from collections import defaultdict
from itertools import combinations, product
from typing import Dict
from stat_functions.add_info import add_info
from neo4j import GraphDatabase

# Setting up logging with formatting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ANSI escape codes for colored output in terminal
green_text = "\033[92m"
orange_text = "\033[93m"
red_text = "\033[91m"
reset_text = "\033[0m"


class Database:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Close the Neo4j driver connection when done to free resources
        self.driver.close()

    def fetch_vehicles_routes_and_roadpoints(self, vehicle_set_id: int) -> Dict[int, Dict]:
        query = """
        MATCH (vs:VehicleSet)-[:CONSISTS_OF]->(vehicle:Vehicle)-[:STARTS_AT]->(start:RouteNode),
        path=(start)-[:NEXT_R*0..]->(end:RouteNode)<-[:ENDS_AT]-(vehicle)
        WHERE id(vs) = $vehicle_set_id
        UNWIND nodes(path) AS routeNode
        MATCH (routeNode)-[:IS_AT]->(roadPoint:RoadPoint)
        WITH vehicle, routeNode, roadPoint
        RETURN id(vehicle) AS vehicleId, 
            collect(id(routeNode)) AS routeNodeIds, 
            collect(id(roadPoint)) AS roadPointIds,
            collect(properties(routeNode)) AS routeNodeProperties,
            collect(properties(roadPoint)) AS roadPointProperties,
            properties(vehicle) AS vehicleProperties

        """
        try:
            with self.driver.session() as session:
                results = session.run(query, vehicle_set_id=vehicle_set_id)
                vehicle_routes_and_roads = {}
                for record in results:
                    vehicle_routes_and_roads[record["vehicleId"]] = {
                        "routeNodeIds": record["routeNodeIds"],
                        "roadPointIds": record["roadPointIds"],
                        "routeNodeProperties": record["routeNodeProperties"],
                        "roadPointProperties": record["roadPointProperties"],
                        "vehicleProperties": record["vehicleProperties"]
                    }
            return vehicle_routes_and_roads
        except Exception as e:
            logger.error(f"{red_text}Failed to fetch vehicle routes: {e}{reset_text}")
            return {}

    def next_route_nodes_at_same_road_point(self, vehicle1, vehicle2, idx1, idx2):
        # Ensure both indices are within the bounds for their respective vehicle's route node IDs
        if idx1 + 1 < len(vehicle1["routeNodeIds"]) and idx2 + 1 < len(vehicle2["routeNodeIds"]):
            # Get the next road point IDs for both vehicles
            next_rp1_id = vehicle1["roadPointIds"][idx1 + 1]
            next_rp2_id = vehicle2["roadPointIds"][idx2 + 1]

            return next_rp1_id == next_rp2_id

        # If one of the indices is out of bounds, or the next road points are not the same, return False
        return False

    # Nodes conditions checks to create / dissolve Platoon
    def no_platoon_at_road_point(self, road_point_id):
        return road_point_id not in self.road_point_to_platoon

    def vehicles_not_in_platoon(self, vehicle1_id, vehicle2_id):
        return (vehicle1_id not in self.vehicle_to_platoon and
                vehicle2_id not in self.vehicle_to_platoon)

    def one_vehicle_in_platoon(self, vehicle1_id, vehicle2_id):
        return (vehicle1_id in self.vehicle_to_platoon) != (vehicle2_id in self.vehicle_to_platoon)

    def one_vehicle_in_platoon_at_specific_route_point(self, vehicle1_id, vehicle2_id, route_point, road_point):
        if route_point in self.route_node_to_platoon:
            return True
        return False

    def both_vehicles_in_same_platoon(self, vehicle1_id, vehicle2_id):
        return (vehicle1_id in self.vehicle_to_platoon and
                vehicle2_id in self.vehicle_to_platoon and
                self.vehicle_to_platoon[vehicle1_id] == self.vehicle_to_platoon[vehicle2_id])

    def platoon_size(self, platoon_id):
        return len(self.platoon_details[platoon_id]['vehicles'])

    # ---------------------------------------------------
    # ---------------------------------------------------
    # ---------------------------------------------------
    # ---------------------------------------------------

    def check_vehicle_compatability(self, v1_properties, v2_properties):
        if v1_properties['technical_requirements'] == v2_properties['technical_requirements'] and \
                v1_properties['legal_requirements'] == v2_properties['legal_requirements']:
            return True
        return False

    def check_route_nodes_compatability(self, r1_properties, r2_properties, rp1_id, rp2_id):
        if r1_properties['departure'] == r2_properties['departure'] and rp1_id == rp2_id:
            return True
        return False

    def extract_route_and_road_data(self, vehicle, index):
        route_node_id = vehicle["routeNodeIds"][index]
        road_point_id = vehicle["roadPointIds"][index]
        route_node_properties = vehicle["routeNodeProperties"][index]
        road_point_properties = vehicle["roadPointProperties"][index]

        return route_node_id, road_point_id, route_node_properties, road_point_properties

    def discover_platoons_python(self, vehicle_set_id: int):
        self.trace = defaultdict(list)  # int -> list[int]
        self.traces_set = set()
        self.nodes = self.fetch_vehicles_routes_and_roadpoints(vehicle_set_id)
        self.platoon_events = {
            "vehicles": {},  # Maps vehicle ID to a list of platoon event IDs
            "route_nodes": {},  # Maps route node ID to a list of platoon event IDs
        }
        self.vehicle_to_platoon = {}  # Maps vehicle ID to its platoon ID
        self.platoon_details = {}  # Maps a platoon ID to its details, including the list of vehicle IDs and route node IDs.
        self.road_point_to_platoon = {}  # Maps a road point ID to its current platoon ID (used to check if there's an available platoon at a road point).
        self.route_node_to_platoon = {}  # Maps a route node ID to its current platoon ID (used to check if a route node is already part of a platoon).

        vehicle_id_pairs = combinations(self.nodes.keys(), 2)
        vehicles_in_set_count = self.nodes.keys()
        # TODO: Add a name to each VehicleSet that corresponds to data_parameters.number_of_different_exp.vehicle_sets_info in experiment.json
        logger.info(
            f"Initiating :Platoon discovery for the {len(vehicles_in_set_count)} vehicles in :VehicleSet (<id>={vehicle_set_id}).")

        # start_timer_trace = datetime.datetime.now()  # Capture start time
        for i, (v1_id, v2_id) in enumerate(vehicle_id_pairs):
            # start_timer_trace = datetime.datetime.now()  # Capture start time

            v1 = self.nodes[v1_id]
            v2 = self.nodes[v2_id]

            
            # if not self.check_vehicle_compatability(v1['properties'], v2['properties']):
            if not self.check_vehicle_compatability(v1['vehicleProperties'], v2['vehicleProperties']):
                continue
            
            for idx1, idx2 in product(range(len(v1["routeNodeIds"])), range(len(v2["routeNodeIds"]))):
                # start_timer_trace = datetime.datetime.now()  # Capture start time
                r1_id, rp1_id, r1_properties, rp1_properties = self.extract_route_and_road_data(v1, idx1)
                r2_id, rp2_id, r2_properties, rp2_properties = self.extract_route_and_road_data(v2, idx2)

                if not self.check_route_nodes_compatability(r1_properties, r2_properties, rp1_id, rp2_id):
                    continue
                # print("---------------------------------------------------")
                # osm_id_r1 = rp1_properties['osm_id']
                # osm_id_r2 = rp2_properties['osm_id']
                # print(f"Checking vehicles {v1_id} and {v2_id} at route nodes {r1_id} (osm_id: {osm_id_r1}) and {r2_id} (osm_id: {osm_id_r2})")
                # Phase 1: Create and Expand Platoons
                if self.next_route_nodes_at_same_road_point(v1, v2, idx1, idx2):
                    if self.vehicles_not_in_platoon(v1_id, v2_id) and self.no_platoon_at_road_point(rp1_id):
                        start_time_create_platoon =datetime.datetime.now()
                        new_platoon_id = self.create_platoon(v1_id, v2_id, r1_id, r2_id, rp1_id)
                        end_time_create_platoon = datetime.datetime.now()
                        duration_create_platoon = (end_time_create_platoon - start_time_create_platoon).total_seconds()
                        add_info("platoonEvent_id", f"{v1_id}_{v2_id}", "platoonEvents_stats.csv")
                        add_info("event_type", "CREATE", "platoonEvents_stats.csv")
                        add_info("vehicle1_id", v1_id, "platoonEvents_stats.csv")
                        add_info("route_node1_id", r1_id, "platoonEvents_stats.csv")
                        add_info("vehicle2_id", v2_id, "platoonEvents_stats.csv")
                        add_info("route_node2_id", r2_id, "platoonEvents_stats.csv")
                        add_info("platoon_id", new_platoon_id, "platoonEvents_stats.csv")
                        add_info("duration", duration_create_platoon, "platoonEvents_stats.csv")

                    elif self.both_vehicles_in_same_platoon(v1_id, v2_id):
                        same_platoon_id = self.vehicle_to_platoon[v1_id]
                        start_time_via = datetime.datetime.now()

                        self.platoon_via(same_platoon_id, r1_id, r2_id, rp1_id, rp2_id)

                        end_time_via = datetime.datetime.now()
                        duration_via = (end_time_via - start_time_via).total_seconds()
                        add_info("platoonEvent_id", f"{v1_id}_{v2_id}", "platoonEvents_stats.csv")
                        add_info("event_type", "VIA", "platoonEvents_stats.csv")
                        add_info("vehicle1_id", v1_id, "platoonEvents_stats.csv")
                        add_info("route_node1_id", r1_id, "platoonEvents_stats.csv")
                        add_info("vehicle2_id", v2_id, "platoonEvents_stats.csv")
                        add_info("route_node2_id", r2_id, "platoonEvents_stats.csv")
                        add_info("platoon_id", same_platoon_id, "platoonEvents_stats.csv")
                        add_info("duration", duration_via, "platoonEvents_stats.csv")

                    # elif self.one_vehicle_in_platoon(v1_id, v2_id):
                    elif self.one_vehicle_in_platoon_at_specific_route_point(v1_id, v2_id, r1_id, rp1_id):
                        v1_at_r1_platoon_id = self.route_node_to_platoon[r1_id]

                        start_time_add_to_platoon = datetime.datetime.now()
                        self.add_to_platoon(v1_at_r1_platoon_id, v2_id, r2_id, rp2_id)

                        end_time_add_to_platoon = datetime.datetime.now()
                        duration_add_to_platoon = (end_time_add_to_platoon - start_time_add_to_platoon).total_seconds()
                        add_info("platoonEvent_id", f"{v1_id}_{v2_id}", "platoonEvents_stats.csv")
                        add_info("event_type", "ADD", "platoonEvents_stats.csv")
                        add_info("vehicle1_id", f"{v1_id}-Present", "platoonEvents_stats.csv")
                        add_info("route_node1_id", r1_id, "platoonEvents_stats.csv")
                        add_info("vehicle2_id", f"{v2_id}-Added", "platoonEvents_stats.csv")
                        add_info("route_node2_id", r2_id, "platoonEvents_stats.csv")
                        add_info("platoon_id", v1_at_r1_platoon_id, "platoonEvents_stats.csv")
                        add_info("duration", duration_add_to_platoon, "platoonEvents_stats.csv")

                # Phase 2: Dismantle and Dissolve Platoons
                elif not self.next_route_nodes_at_same_road_point(v1, v2, idx1, idx2):
                    if self.both_vehicles_in_same_platoon(v1_id, v2_id):
                        same_platoon_id = self.vehicle_to_platoon[v1_id]
                        if self.platoon_size(same_platoon_id) > 2:

                            start_remove_from_platoon = datetime.datetime.now()
                            self.remove_from_platoon(same_platoon_id, v1_id, r1_id, rp1_id)

                            end_remove_from_platoon = datetime.datetime.now()
                            duration_remove_from_platoon = (end_remove_from_platoon - start_remove_from_platoon).total_seconds()
                            add_info("platoonEvent_id", f"{v1_id}_{v2_id}", "platoonEvents_stats.csv")
                            add_info("event_type", "REMOVE", "platoonEvents_stats.csv")
                            add_info("vehicle1_id", f"{v1_id}-Removed", "platoonEvents_stats.csv")
                            add_info("route_node1_id", r1_id, "platoonEvents_stats.csv")
                            add_info("vehicle2_id", f"{v2_id}-Present", "platoonEvents_stats.csv")
                            add_info("route_node2_id", r2_id, "platoonEvents_stats.csv")
                            add_info("platoon_id", same_platoon_id, "platoonEvents_stats.csv")
                            add_info("duration", duration_remove_from_platoon, "platoonEvents_stats.csv")

                        elif self.platoon_size(same_platoon_id) == 2:

                            start_dissolve_platoon = datetime.datetime.now()
                            self.dissolve_platoon(same_platoon_id, r1_id, r2_id, rp1_id, v1_id, v2_id)
                            end_dissolve_platoon = datetime.datetime.now()
                            duration_dissolve_platoon = (end_dissolve_platoon - start_dissolve_platoon).total_seconds()
                            add_info("platoonEvent_id", f"{v1_id}_{v2_id}", "platoonEvents_stats.csv")
                            add_info("event_type", "DISSOLVE", "platoonEvents_stats.csv")
                            add_info("vehicle1_id", v1_id, "platoonEvents_stats.csv")
                            add_info("route_node1_id", r1_id, "platoonEvents_stats.csv")
                            add_info("vehicle2_id", v2_id, "platoonEvents_stats.csv")
                            add_info("route_node2_id", r2_id, "platoonEvents_stats.csv")
                            add_info("platoon_id", same_platoon_id, "platoonEvents_stats.csv")
                            add_info("duration", duration_dissolve_platoon, "platoonEvents_stats.csv")
                            
        # end_timer_trace = datetime.datetime.now()  # Capture start time
        # duration = end_timer_trace - start_timer_trace  # Calculate duration
        # add_info("platoon_duration3", str(duration), "platoon_stats.csv")

        logger.info(f"Finished discovering :Platoons for :VehicleSet (<id>={vehicle_set_id})")
        # print("Trace set from database***:", self.traces_set)
        # print("Trace from database ++++:",self.trace)
        return self.traces_set, self.trace

    def create_platoon(self, vehicle1_id, vehicle2_id, route_node1_id, route_node2_id, road_point_id):
        query = """
            CREATE (platoon:Platoon {size_max: 99})
            CREATE (event:PlatoonEvent {timestamp: $timestamp})
            WITH platoon, event
            MATCH (r1:RouteNode) WHERE id(r1) = $route_node1_id
            MATCH (r2:RouteNode) WHERE id(r2) = $route_node2_id
            CREATE (platoon)-[:CREATE]->(event)
            CREATE (event)-[:HAPPENS_AT]->(r1)
            CREATE (event)-[:HAPPENS_AT]->(r2)
            RETURN id(platoon) AS platoonId
            """
        params = {
            'timestamp': datetime.datetime.now().isoformat(),
            'route_node1_id': route_node1_id,
            'route_node2_id': route_node2_id
        }
        try:
            with self.driver.session() as session:
                result = session.run(query, params)
                # print(f"Neo4j driver: Created platoon successfully")
                record = result.single()
                if record:
                    new_platoon_id = record["platoonId"]
                    # print("Created new_platoon_id = ", new_platoon_id)
                    # Update local data structures
                    self.vehicle_to_platoon[vehicle1_id] = new_platoon_id
                    self.vehicle_to_platoon[vehicle2_id] = new_platoon_id
                    self.road_point_to_platoon[road_point_id] = new_platoon_id
                    self.route_node_to_platoon[route_node1_id] = new_platoon_id
                    self.route_node_to_platoon[route_node2_id] = new_platoon_id
                    self.platoon_details[new_platoon_id] = {
                        'vehicles': {vehicle1_id, vehicle2_id},
                        'route_nodes': {route_node1_id, route_node2_id}
                    }
                    # print(f"(:CREATE) Created platoon (id = {new_platoon_id}) between vehicles_id {vehicle1_id} and {vehicle2_id} at roadpoint {road_point_id} (route nodes ids {route_node1_id}  and {route_node2_id})")
                    # logger.info(f"{green_text}Created :Platoon (<id>={new_platoon_id}) between :Vehicles (<id>={vehicle1_id}) and (<id>={vehicle2_id}) at :RoadPoint (<id>={road_point_id}) with :RouteNodes (<id>={route_node1_id}) and (<id>={route_node2_id}){reset_text}")

                    self.trace[new_platoon_id].append(f"(pl)-[:CREATE]->(e)")
                    self.traces_set.add(new_platoon_id)
                    return new_platoon_id
                else:
                    logger.error(
                        f"{red_text}Failed to load newly created platoon ID between vehicles {vehicle1_id} and {vehicle2_id} at route nodes {route_node1_id} and {route_node2_id}.{reset_text}")

        except Exception as e:
            logger.error(
                f"{red_text}Failed to create :Platoon for :Vehicles (<id>={vehicle1_id}) and (<id>={vehicle2_id}) at :RoadPoint (<id>={road_point_id}): {e}{reset_text}")
            return -1

    def dissolve_platoon(self, platoon_id, route_node1_id, route_node2_id, road_point1_id, vehicle1_id, vehicle2_id):
        query = """
            MATCH (platoon:Platoon) WHERE id(platoon) = $platoon_id
            MATCH (rn1:RouteNode) WHERE id(rn1) = $route_node1_id
            MATCH (rn2:RouteNode) WHERE id(rn2) = $route_node2_id
            CREATE (platoon)-[:DISSOLVE]->(event:PlatoonEvent {timestamp: $timestamp})
            CREATE (event)-[:HAPPENS_AT]->(rn1)
            CREATE (event)-[:HAPPENS_AT]->(rn2)
        """
        params = {
            'platoon_id': platoon_id,
            'route_node1_id': route_node1_id,
            'route_node2_id': route_node2_id,
            'timestamp': datetime.datetime.now().isoformat()
        }
        try:
            with self.driver.session() as session:
                session.run(query, params)
                # print("Neo4j driver: Dissolved platoon successfully.")
        except Exception as e:
            logger.error(
                f"{red_text}Failed to dissolve platoon {platoon_id} at route nodes {route_node1_id} and {route_node2_id}: {e}{reset_text}")

        # Update local data structures
        # Since both route points happen at the same road point (confirmed by the compatibility check), we only need to update one of them
        self.road_point_to_platoon[road_point1_id] = platoon_id
        # self.road_point_to_platoon[road_point2_id] = platoon_id
        self.route_node_to_platoon[route_node1_id] = platoon_id
        self.route_node_to_platoon[route_node2_id] = platoon_id
        # commenting out since we might still need to extend the vehicles in this platoon when v1 is compared with v(n+1) even if v1xv(n) are dissolved
        # self.platoon_details.pop(platoon_id)
        self.vehicle_to_platoon.pop(vehicle1_id)
        self.vehicle_to_platoon.pop(vehicle2_id)
        # print(f"(:DISSOLVE) Dissolved platoon (id = {platoon_id}) between vehicles {vehicle1_id} and {vehicle2_id} at at roadpoint {road_point1_id} (route nodes {route_node1_id} and {route_node2_id})")
        self.trace[platoon_id].append(f"(pl)-[:DISSOLVE]->(e)")

    def add_to_platoon(self, existing_platoon_id, vehicle_id, route_node_id, road_point_id):
        # Database creation of Platoon and PlatoonEvent nodes and relationships
        # (This would be a good place for a transaction to ensure data integrity)
        query = """
            MATCH (platoon:Platoon) WHERE id(platoon) = $existing_platoon_id
            MATCH (rn:RouteNode) WHERE id(rn) = $route_node_id
            CREATE (platoon)-[:ADD]->(event:PlatoonEvent {timestamp: $timestamp})
            CREATE (event)-[:HAPPENS_AT]->(rn)
        """
        params = {
            'existing_platoon_id': existing_platoon_id,
            'timestamp': datetime.datetime.now().isoformat(),
            'route_node_id': route_node_id
        }
        try:
            with self.driver.session() as session:
                session.run(query, params)
                # print(f"Neo4j driver: Added {vehicle_id} :ADD to platoon {existing_platoon_id} successfully.")
        except Exception as e:
            logger.error(
                f"{red_text}Failed to add vehicle {vehicle_id} to platoon {existing_platoon_id} at route node {route_node_id}: {e}{reset_text}")

        # Update local data structures
        self.vehicle_to_platoon[vehicle_id] = existing_platoon_id
        self.platoon_details[existing_platoon_id]['vehicles'].add(vehicle_id)
        self.platoon_details[existing_platoon_id]['route_nodes'].add(route_node_id)
        # No need to update road_point_to_platoon since the route node happens at the same road point where a platoon already exists
        self.route_node_to_platoon[route_node_id] = existing_platoon_id
        # print(f"(:ADD) Added vehicle {vehicle_id} to platoon {existing_platoon_id} at roadpoint {road_point_id} (route node {route_node_id})")
        self.trace[existing_platoon_id].append(f"(pl)-[:ADD]->(e)")

    def platoon_via(self, existing_platoon_id, route_node1_id, route_node2_id, road_point1_id, road_point2_id):
        # creates a :VIA relationship between the platoon and the route nodes
        query = """
            MATCH (platoon:Platoon) WHERE id(platoon) = $existing_platoon_id
            MATCH (rn1:RouteNode) WHERE id(rn1) = $route_node1_id
            MATCH (rn2:RouteNode) WHERE id(rn2) = $route_node2_id
            CREATE (platoon)-[:VIA]->(eventrn1:PlatoonEvent {timestamp: $timestamp})
            CREATE (eventrn1)-[:HAPPENS_AT]->(rn1)
            CREATE (eventrn2)-[:HAPPENS_AT]->(rn2)
        """
        params = {
            'existing_platoon_id': existing_platoon_id,
            'route_node1_id': route_node1_id,
            'route_node2_id': route_node2_id,
            'timestamp': datetime.datetime.now().isoformat()
        }
        try:
            with self.driver.session() as session:
                session.run(query, params)
                # print(f"Neo4j driver: Added :VIA to platoon successfully at route nodes {route_node1_id} and {route_node2_id}.")
        except Exception as e:
            logger.error(
                f"{red_text}Failed to create :VIA relation for platoon {existing_platoon_id} at route nodes {route_node1_id} and {route_node2_id}: {e}{reset_text}")

        # Update local data structures
        self.platoon_details[existing_platoon_id]['route_nodes'].add(route_node1_id)
        self.platoon_details[existing_platoon_id]['route_nodes'].add(route_node2_id)
        # Since both route points happen at the same road point (confirmed by the compatibility check), we only need to update one of them
        self.road_point_to_platoon[road_point1_id] = existing_platoon_id
        # self.road_point_to_platoon[road_point2_id] = existing_platoon_id
        self.route_node_to_platoon[route_node1_id] = existing_platoon_id
        self.route_node_to_platoon[route_node2_id] = existing_platoon_id
        # print(f"(:VIA) platoon {existing_platoon_id} is :VIA at roadpoint {road_point1_id} (route nodes {route_node1_id} and {route_node2_id})")
        self.trace[existing_platoon_id].append(f"(pl)-[:VIA]->(e)")

    def remove_from_platoon(self, platoon_id, vehicle_id, route_node_id, road_point_id):
        query = """
            MATCH (platoon:Platoon) WHERE id(platoon) = $platoon_id
            MATCH (rn:RouteNode) WHERE id(rn) = $route_node_id
            CREATE (platoon)-[:REMOVE]->(event:PlatoonEvent {timestamp: $timestamp})
            CREATE (event)-[:HAPPENS_AT]->(rn)
        """
        params = {
            'platoon_id': platoon_id,
            'route_node_id': route_node_id,
            'timestamp': datetime.datetime.now().isoformat()
        }
        try:
            with self.driver.session() as session:
                session.run(query, params)
                # print(f"Neo4j driver: Removed vehicle {vehicle_id} from platoon {platoon_id} successfully.")
        except Exception as e:
            logger.error(
                f"{red_text}Failed to remove vehicle {vehicle_id} from platoon {platoon_id} at route node {route_node_id}: {e}{reset_text}")

        # Update local data structures
        self.vehicle_to_platoon.pop(vehicle_id)
        self.platoon_details[platoon_id]['vehicles'].remove(vehicle_id)
        # For the next line, I would argue that the route node should say linked to the platoon since that route node is tied to the platoon
        # However, one should ask is platoon_details[platoon_id]['route_nodes'] even needed? seems not. It's never checked.
        # self.platoon_details[platoon_id]['route_nodes'].remove(route_node_id)
        # print(f"(:REMOVE) Removed vehicle {vehicle_id} from platoon {platoon_id} at roadpoint {road_point_id} (route node {route_node_id})")
        self.trace[platoon_id].append(f"(pl)-[:REMOVE]->(e)")
