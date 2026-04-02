from importlib.resources import path
from stat_functions.add_info import add_info
from util.databasecontainer import DatabaseContainer
from util.cmd import CMD
from typing import List, Tuple
import time
from util.configuration import Configuration
from random import randint
import random
import datetime

import logging

# Setting up logging with formatting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ANSI escape codes for colored output in terminal
green_text = "\033[92m"
orange_text = "\033[93m"
red_text = "\033[91m"
reset_text = "\033[0m"



class Database:
    def __init__(self):
        raise NotImplementedError("static")

    @staticmethod
    def clean_vehicle_set(vehicle_set_id: int) -> None:
        pass

    @staticmethod
    def check_vehicle_set():
        # TODO: parameterise query
        with DatabaseContainer.driver.session() as session:
            tx = session.begin_transaction()
            query = "MATCH (vs:VehicleSetTest)-[:TEST_REL]->(v:VehicleTest) WITH vs, v " \
                    "OPTIONAL MATCH (e:RN_TEST)-[:SP_END]-(v)-[:SP_START]->(s:RN_TEST) WITH vs, v, e, s " \
                    "OPTIONAL MATCH p1=(s)-[r:NEXT_TEST*]->(e) WITH vs, v, p1 " \
                    "OPTIONAL MATCH (start)-[:STARTATLOCATION]-(v)-[:ENDATLOCATION]-(end) WITH vs, v, p1, start, end  "\
                    "CALL apoc.algo.aStar(start, end, 'NEIGHBOUR>', 'distance_meter','lat','lon') YIELD path as p2 " \
                    "WITH vs, v, p1, p2 " \
                    "RETURN length(relationships(p1)) as l1, length(relationships(p2)) as l2, vs, v, " \
                    "reduce(dist1 = 0, rel1 IN relationships(p1)| dist1 + rel1.distance) AS dist1, " \
                    "reduce(dist2 = 0, rel2 IN relationships(p2)| dist2 + rel2.distance) AS dist2"

            results = tx.run(query)

            for result in results:
                print(result)

    @staticmethod
    def create_vehicle_set_by_location_ids(vehicle_location_ids: List[Tuple[int, int]]) -> int:
        number_of_vehicles = len(vehicle_location_ids)
        vehicle_set_id = Database._create_vehicle_set("custom_nodes", number_of_vehicles)

        Database.update_vehicle_set_by_location_ids(vehicle_set_id, vehicle_location_ids)

        # with DatabaseContainer.driver.session() as session:
        #     tx = session.begin_transaction()
        #     for vehicle_location_id in vehicle_location_ids:
        #
        #         start_id = vehicle_location_id[0]
        #         end_id = vehicle_location_id[1]
        #
        #         query = "MATCH (vs:" + CMD.vehicle_set_label + ") WHERE id(vs) = "+ str(vehicle_set_id) +" CREATE (vs)-[:" + CMD.vehicle_in_set_rel + "]->(v:"+ CMD.vehicle_label +") WITH v MATCH (n1:" + CMD.road_label + "), (n2:" + CMD.road_label + ") WHERE id(n1)=" + str(start_id) + " AND id(n2) = " + str(end_id) + " CREATE (n1)<-[:" + CMD.vehicle_start_rel + "]-(v)-[:"+ CMD.vehicle_end_rel +"]->(n2) WITH n1, n2, v " \
        #         "CALL apoc.algo.aStar(n1, n2, '" + CMD.road_rel + ">', 'distance_meter','lat','lon') YIELD path, weight " \
        #         "WITH weight, n1, v, nodes(path) as path_list, nodes(path)[0] as first, nodes(path)[-1] as last " \
        #         "FOREACH (pn IN path_list[1..length(path_list)-1] | CREATE (pn)<-[:" + CMD.route_rel + "{ veh_id: id(v)}]-(:" + CMD.route_label + ")) " \
        #         "CREATE (first)<-[:" + CMD.route_rel + "{ veh_id: id(v)}]-(:" + CMD.route_label + ")<-[:" + CMD.sp_rel_start + "]-(v)  " \
        #         "CREATE (last)<-[:" + CMD.route_rel + "{ veh_id: id(v)}]-(:" + CMD.route_label + ")<-[:" + CMD.sp_rel_end + "]-(v) " \
        #         "SET v.shortest_path_distance = weight  WITH v, " \
        #         "EXTRACT(i IN RANGE(0, LENGTH(path_list) - 2) | [path_list[i], path_list[i+1]]) AS pairs " \
        #         "UNWIND pairs as pair WITH v, pair[0] as l1, pair[1] as l2, pair WITH v, l1, l2 " \
        #         "MATCH (l1)-[r:" + CMD.road_rel + "]-(l2) MATCH (l1)-[lc1:" + CMD.route_rel + "]-(rn1), (l2)-[lc2:" + CMD.route_rel + "]-(rn2) WHERE lc1.veh_id = id(v) AND lc2.veh_id=id(v)  " \
        #         "CREATE (rn1)-[:" + CMD.next_route_rel + "{distance:r.distance, distance_meter:r.distance_meter}]->(rn2)"
        #         tx.run(query)
        #         print(query)
        #     tx.commit()

        return vehicle_set_id
    
    def create_vehicle_set_by_location_ids_trace(vehicle_location_ids: List[Tuple[int, int]]) -> int:
        number_of_vehicles = len(vehicle_location_ids)
        vehicle_set_id = Database._create_vehicle_set("custom_nodes", number_of_vehicles)
        # doesn't work, the astar throws a ValueError: Values of type <class 'neo4j.graph.Node'> are not supported(2025). Now it works fine😁 (2026)
        with DatabaseContainer.driver.session() as session:
            start_time = datetime.datetime.now()
            # Start a Neo4j transaction
            with session.begin_transaction() as tx:
                for start_id, end_id in vehicle_location_ids:
                    try:
                        # Assure that the start and end points exist in the database
                        # Find the start and end RoadPoints
                        start_point = tx.run(
                            "MATCH (n:RoadPoint) WHERE id(n)=$start_id RETURN n", start_id=start_id
                        ).single()

                        if not start_point:
                            logger.error(f"{red_text}Start point with id {start_id} does not exist in the current database.{reset_text}")
                            raise RuntimeError(f"Start point with id {start_id} not found.")

                        end_point = tx.run(
                            "MATCH (n:RoadPoint) WHERE id(n)=$end_id RETURN n", end_id=end_id
                        ).single()

                        if not end_point:
                            logger.error(f"{red_text}End point with id {end_id} does not exist in the current database.{reset_text}")
                            raise RuntimeError(f"End point with id {end_id} not found.")

                        # Create a new vehicle with a random route between the start and end points
                        vehicle_properties = {
                            "earliest_departure": datetime.datetime.now().isoformat(),
                            "latest_arrival": (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat(),
                            "speed_min": 30,
                            "speed_opt": 60,
                            "speed_max": 90,
                            "technical_requirements": "standard",
                            "legal_requirements": "standard"
                        }
                        
                        # TODO update vehicle_properties with correct timing
                        start_time_vehicle = datetime.datetime.now()
                        vehicle_node = tx.run(f"""
                            MATCH (vs:{CMD.vehicle_set_label}) WHERE id(vs) = {vehicle_set_id}
                            MATCH (start:RoadPoint), (end:RoadPoint) WHERE id(start) = $start_id AND id(end) = $end_id
                            CREATE (vs)-[:{CMD.vehicle_in_set_rel}]->(v:Vehicle {{properties}})
                            CREATE (v)-[:ORIGIN]->(start)
                            CREATE (v)-[:DESTINATION]->(end)
                            RETURN v
                        """, properties=vehicle_properties, start_id=start_id, end_id=end_id).single()[0]

                        end_time_vehicle = datetime.datetime.now()
                        duration_vehicle = (end_time_vehicle - start_time_vehicle).total_seconds()
                        
                        add_info("vehicle_id", vehicle_node.id, "vehicle_stats.csv")
                        add_info("vehicle_creation_time", duration_vehicle, "vehicle_stats.csv")
                        add_info("legal_requirements", vehicle_properties["legal_requirements"], "vehicle_stats.csv")
                        add_info("technical_requirements", vehicle_properties["technical_requirements"], "vehicle_stats.csv")  
                        add_info("average_speed", (vehicle_properties["speed_min"] + vehicle_properties["speed_opt"] + vehicle_properties["speed_max"]) / 3, "vehicle_stats.csv")
                        add_info("earliest_departure", vehicle_properties["earliest_departure"], "vehicle_stats.csv")
                        add_info("latest_arrival", vehicle_properties["latest_arrival"], "vehicle_stats.csv")
                        add_info("vehicle_set_id", vehicle_set_id, "vehicle_stats.csv")
                        # add_info("type", "custom", "vehicle_stats.csv")
                        

                        # Calculate the shortest path using the aStar algorithm
                        result = tx.run("""
                            MATCH (start:RoadPoint), (end:RoadPoint)
                            WHERE id(start) = $start_id AND id(end) = $end_id
                            CALL apoc.algo.aStar(start, end, 'ROAD_SEGMENT', 'distance_meter', 'lat', 'lon') YIELD path, weight
                            RETURN nodes(path), weight
                        """, start_id=start_id, end_id=end_id).single()

                        path = result[0]
                        weight = result['weight']

                        Database.create_route_nodes(tx, path, vehicle_node)
                    except Exception as e:
                        logger.error(f"{red_text}Failed to process vehicle from {start_id} to {end_id}: {e}{reset_text}")
                        raise e

                tx.commit()
                end_time = datetime.datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.info(f"{green_text}Created {number_of_vehicles} vehicle(s) in a :VehicleSet (<id>={vehicle_set_id}) in {duration} seconds.{reset_text}")
                add_info("vehicle_set_id", vehicle_set_id, "vehicleSet_stats.csv")
                add_info("number_of_vehicles", number_of_vehicles, "vehicleSet_stats.csv")
                add_info("creation_time_laps", duration, "vehicleSet_stats.csv")
                add_info("type", "random", "vehicleSet_stats.csv")

        return vehicle_set_id

    @staticmethod
    def update_vehicle_set_by_location_ids_DEP(vehicle_set_id: int, vehicle_location_ids: List[Tuple[int, int]]) -> None:
        number_of_vehicles = len(vehicle_location_ids)

        with DatabaseContainer.driver.session() as session:
            tx = session.begin_transaction()
            for vehicle_location_id in vehicle_location_ids:

                start_id = vehicle_location_id[0]
                end_id = vehicle_location_id[1]

                
                query = "MATCH (vs:" + CMD.vehicle_set_label + ") WHERE id(vs) = "+ str(vehicle_set_id) +" CREATE (vs)-[:" + CMD.vehicle_in_set_rel + "]->(v:"+ CMD.vehicle_label +") WITH v MATCH (n1:" + CMD.road_label + "), (n2:" + CMD.road_label + ") WHERE id(n1)=" + str(start_id) + " AND id(n2) = " + str(end_id) + " CREATE (n1)<-[:" + CMD.vehicle_start_rel + "]-(v)-[:"+ CMD.vehicle_end_rel +"]->(n2) WITH n1, n2, v " \
                "CALL apoc.algo.aStar(n1, n2, '" + CMD.road_rel + ">', 'distance_meter','lat','lon') YIELD path, weight " \
                "WITH weight, n1, v, nodes(path) as path_list, nodes(path)[0] as first, nodes(path)[-1] as last " \
                "FOREACH (pn IN path_list[1..length(path_list)-1] | CREATE (pn)<-[:" + CMD.route_rel + "{ veh_id: id(v)}]-(:" + CMD.route_label + ")) " \
                "CREATE (first)<-[:" + CMD.route_rel + "{ veh_id: id(v)}]-(:" + CMD.route_label + ")<-[:" + CMD.sp_rel_start + "]-(v)  " \
                "CREATE (last)<-[:" + CMD.route_rel + "{ veh_id: id(v)}]-(:" + CMD.route_label + ")<-[:" + CMD.sp_rel_end + "]-(v) " \
                "SET v.shortest_path_distance = weight  WITH v, " \
                "EXTRACT(i IN RANGE(0, LENGTH(path_list) - 2) | [path_list[i], path_list[i+1]]) AS pairs " \
                "UNWIND pairs as pair WITH v, pair[0] as l1, pair[1] as l2, pair WITH v, l1, l2 " \
                "MATCH (l1)-[r:" + CMD.road_rel + "]-(l2) MATCH (l1)-[lc1:" + CMD.route_rel + "]-(rn1), (l2)-[lc2:" + CMD.route_rel + "]-(rn2) WHERE lc1.veh_id = id(v) AND lc2.veh_id=id(v)  " \
                "CREATE (rn1)-[:" + CMD.next_route_rel + "{distance:r.distance, distance_meter:r.distance_meter}]->(rn2)"
                
                print("\nQuery for update_vehicle_set_by_location_ids:\n", query, "\n\n\n")
                tx.run(query)


    @staticmethod
    def update_vehicle_set_by_location_ids(vehicle_set_id: int, vehicle_location_ids: List[Tuple[int, int]]) -> None:
        """
        Updates a vehicle set by adding vehicles based on provided start and end location IDs.
        Each vehicle is connected to start and end locations, a shortest path is calculated between these points,
        and route relationships are created along the path, each tagged with the vehicle's ID.
        
        :param vehicle_set_id: ID of the vehicle set to be updated.
        :param vehicle_location_ids: List of tuples containing start and end location IDs for each vehicle.
        """
        with DatabaseContainer.driver.session() as session:
            tx = session.begin_transaction()

            for start_id, end_id in vehicle_location_ids:
                # Vehicle and set relation
                create_vehicle = (
                    f"MATCH (vs:{CMD.vehicle_set_label}) WHERE id(vs) = {vehicle_set_id} "
                    f"CREATE (vs)-[:{CMD.vehicle_in_set_rel}]->(v:{CMD.vehicle_label}) "
                    f"RETURN id(v) AS vehicle_id"
                )

                # Execute the vehicle creation query and get the vehicle_id
                vehicle_id_result = tx.run(create_vehicle).single()
                vehicle_id = vehicle_id_result['vehicle_id']

                # Connect vehicle to start and end points
                connect_start_end = (
                    f"MATCH (v:{CMD.vehicle_label}), (start:{CMD.road_label}), (end:{CMD.road_label}) "
                    f"WHERE id(v) = {vehicle_id} AND id(start) = {start_id} AND id(end) = {end_id} "
                    f"CREATE (start)<-[:{CMD.vehicle_start_rel}]-(v)-[:{CMD.vehicle_end_rel}]->(end) "
                )

                path_finding_and_route_creation = (
                    f"WITH v, start, end "
                    f"CALL apoc.algo.aStar(start, end, '{CMD.road_rel}', 'distance', 'lat', 'lon') YIELD path, weight "

                    f"WITH v, weight, nodes(path) AS pathNodes "
                    f"UNWIND range(1, size(pathNodes) - 2) AS idx "
                    f"WITH v, weight, pathNodes, pathNodes[idx] AS currentNode "
                    f"MERGE (currentNode)-[r:LOC]->(:RouteNodeTemp {{veh_id: id(v)}}) "

                    f"WITH v, weight, pathNodes[0] AS firstNode, pathNodes[size(pathNodes)-1] AS lastNode, pathNodes "
                    f"MERGE (firstNode)<-[:{CMD.route_rel}{{veh_id: id(v)}}]-(:{CMD.route_label})<-[:{CMD.sp_rel_start}]-(v) "
                    f"MERGE (lastNode)<-[:{CMD.route_rel}{{veh_id: id(v)}}]-(:{CMD.route_label})<-[:{CMD.sp_rel_start}]-(v) "
                    
                    f"WITH DISTINCT v, weight, pathNodes "
                    f"SET v.shortest_path_distance = weight "
                    f"WITH v, pathNodes "
                    f"UNWIND range(0, size(pathNodes) - 2) AS i "
                    f"WITH v, pathNodes, pathNodes[i] AS currentNode, pathNodes[i + 1] AS nextNode "
                    f"MATCH (currentNode)-[r:{CMD.road_rel}]->(nextNode) "
                    f"MATCH (currentNode)-[r:{CMD.route_rel}]->(rn1:{CMD.route_label}), (nextNode)-[:{CMD.route_rel}]->(rn2:{CMD.route_label}) "
                    f"WHERE rn1.veh_id = id(v) AND rn2.veh_id = id(v) "
                    f"CREATE (rn1)-[:{CMD.next_route_rel}{{distance: r.distance, distance_meter: r.distance_meter}}]->(rn2) "
                )



                print("\nQuery for update_vehicle_set_by_location_ids:\n", connect_start_end + path_finding_and_route_creation, "\n")
                # Run the query for connecting the vehicle to start and end, path finding, and route creation
                tx.run(connect_start_end + path_finding_and_route_creation)
                #print("******************************\n******************************\n******************************\n")

            tx.commit()


    @staticmethod
    def _create_vehicle_set(distribution: str, number_of_vehicles: int) -> int:
        with DatabaseContainer.driver.session() as session:
            tx = session.begin_transaction()
            #query = "CREATE (n:" + CMD.vehicle_set_label + "{distribution: '" + distribution + "', size: toInteger(" + str(number_of_vehicles) + ")}) RETURN id(n) AS vs_id "
            query = f"""
            CREATE (n:{CMD.vehicle_set_label}:TraceSet {{
            distribution: '{distribution}',
            size: toInteger({number_of_vehicles})
            }})
            RETURN id(n) AS vs_id
            """
            #print("query for _create_vehicle_set: \n", query)
            results = tx.run(query)
            result = results.single()
            vehicle_set_id = result.get("vs_id")
            #print(f"Created vehicle set with ID {vehicle_set_id}")
            tx.commit()
        return vehicle_set_id

    @staticmethod
    def create_random_vehicle_set_DEPRECATED(number_of_vehicles: int) -> int:
        """
        creation of random distributed vehicle for given number of vehicles
        :param number_of_vehicles: number of vehicles
        :return: vehicle set id of created vehicle set
        """

        vehicle_set_id = Database._create_vehicle_set("random", number_of_vehicles)

        with DatabaseContainer.driver.session() as session:
            start_time = time.time()

            """ Creation of random vehicles
                aStar produces wrong path if the relation between coordinates(lat lon) and distance not correct! 
            """
            tx = session.begin_transaction()
            # extend line 138
            # "CREATE (vs)-[r:" + CMD.vehicle_in_set_rel + "]->(v:" + CMD.vehicle_label + ")\n" \
            # with technical and legal requirement for the trace_discovery algorithms.
            query = "MATCH (vs:" + CMD.vehicle_set_label + ") WHERE id(vs) = " + str(vehicle_set_id) + "\n" \
                    "MATCH (n:" + CMD.road_label + ") WITH vs, COUNT(n) AS road_number\n" \
                    "UNWIND range(1, " + str(number_of_vehicles) + ") AS i\n" \
                    "WITH vs, toInteger(floor(rand()*(road_number-0.000001))) AS rnd_1, toInteger(floor(rand()*(road_number-1.000001))) AS rnd_2\n" \
                    "CALL apoc.periodic.iterate(\n" \
                    "'MATCH (vs) WHERE ID(vs) = ' + ID(vs) + ' RETURN vs',\n" \
                    "'MATCH (n1:" + CMD.road_label + ") WITH vs, n1 SKIP ' + rnd_1 + ' LIMIT 1\n" \
                    "MATCH (n2:" + CMD.road_label + ") WHERE ID(n2) <> ID(n1) WITH vs, n1, n2 SKIP ' + rnd_2 + ' LIMIT 1\n" \
                    "CREATE (vs)-[r:" + CMD.vehicle_in_set_rel + "]->(v:" + CMD.vehicle_label + ")\n" \
                    "CREATE (n2)<-[:" + CMD.vehicle_end_rel + "]-(v)-[:" + CMD.vehicle_start_rel + "]->(n1)\n" \
                    "WITH vs, v, n1, n2\n" \
                    "CALL apoc.algo.aStar(n1, n2, \"" + CMD.road_rel + ">\", \"distance_meter\", \"lat\", \"lon\") YIELD path, weight\n" \
                    "WITH vs, v, n1, n2, weight, nodes(path) as path_list, nodes(path)[0] as first, nodes(path)[-1] as last\n" \
                    "FOREACH (pn IN path_list[1..length(path_list)-1] | CREATE (pn)<-[:LOC{ veh_id: id(v)}]-(:RouteNodeTemp))\n" \
                    "CREATE (first)<-[:LOC{ veh_id: id(v)}]-(:RouteNodeTemp)<-[:SP_START]-(v)\n" \
                    "CREATE (last)<-[:LOC{ veh_id: id(v)}]-(:RouteNodeTemp)<-[:SP_END]-(v)\n" \
                    "SET v.shortest_path_distance = weight  WITH v,\n" \
                    "EXTRACT(i IN RANGE(0, LENGTH(path_list) - 2) | [path_list[i], path_list[i+1]]) AS pairs\n" \
                    "UNWIND pairs as pair WITH v, pair[0] as l1, pair[1] as l2, pair WITH v, l1, l2\n" \
                    "MATCH (l1)-[r:" + CMD.road_rel + "]-(l2) MATCH (l1)-[lc1:" + CMD.route_rel + "]-(rn1), (l2)-[lc2:" + CMD.route_rel + "]-(rn2) WHERE lc1.veh_id = id(v) AND lc2.veh_id=id(v)\n" \
                    "CREATE (rn1)-[:" + CMD.next_route_rel + "{distance:r.distance, distance_meter:r.distance_meter}]->(rn2)',\n" \
                    "{batchSize:1, parallel:true}) YIELD batches, total\n" \
                    "RETURN COUNT(*)"
            print("query for create_random_vehicle_set:\n", query)
            tx.run(query)
            # Clean up of temp properties
            query = "MATCH ()-[r:" + CMD.route_rel + "]->() REMOVE r.veh_id"
            tx.run(query)
            tx.commit()

            # Database.check_vehicle_set()
            print("* Created {count} vehicle(s) in {time} seconds.".format(count=number_of_vehicles,
                                                                          time=round(time.time() - start_time, 2)))

            return vehicle_set_id

    @staticmethod
    def create_random_vehicle_set(number_of_vehicles: int) -> int:
        """
        Creation of randomly distributed vehicles for a given number of vehicles.
        :param number_of_vehicles: The number of vehicles to create.
        :return: The vehicle set ID of the created vehicle set.
        """
        vehicle_set_id = Database._create_vehicle_set("random", number_of_vehicles)

        with DatabaseContainer.driver.session() as session:
            start_time = datetime.datetime.now()
            tx = session.begin_transaction()

            # Get the total number of road points to ensure random selection within bounds
            road_count_query = "MATCH (n:" + CMD.road_label + ") RETURN COUNT(n) AS road_number"
            road_number = tx.run(road_count_query).single()[0]
            if road_number < 2:
                logger.error(f"{red_text}Road network contains insufficient points. Found {road_number} road point(s). At least 2 are required.{reset_text}")
                raise ValueError("The road network must contain at least two road points to create vehicles.")

            for _ in range(number_of_vehicles):
                rnd_1 = randint(0, road_number - 1)
                rnd_2 = randint(0, road_number - 1)
                
                # Ensure rnd_2 is different from rnd_1
                while rnd_2 == rnd_1:
                    rnd_2 = randint(0, road_number - 1)

                # Construct Cypher query using the logical structure from the example
                create_vehicle_query = (
                    f"MATCH (vs:{CMD.vehicle_set_label}) WHERE id(vs) = {vehicle_set_id} "
                    f"MATCH (start:{CMD.road_label}) WITH vs, collect(start) AS starts "
                    f"MATCH (end:{CMD.road_label}) WITH vs, starts, collect(end) AS ends "
                    f"WITH vs, starts[toInteger(rand() * size(starts))] AS start, ends[toInteger(rand() * size(ends))] AS end "
                    f"CREATE (vs)-[:{CMD.vehicle_in_set_rel}]->(v:{CMD.vehicle_label})-[:{CMD.vehicle_start_rel}]->(start), "
                    f"(v)-[:{CMD.vehicle_end_rel}]->(end) "
                    f"WITH start, end, v "
                    f"CALL apoc.algo.aStar(start, end, '{CMD.road_rel}', 'distance_meter', 'lat', 'lon') YIELD path, weight "
                    f"SET v.shortest_path_distance = weight"
                )
                tx.run(create_vehicle_query)
            tx.commit()
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()

        logger.info(f"{green_text}Created {number_of_vehicles} vehicle(s) in the set with ID {vehicle_set_id}.{reset_text}")
        add_info("vehicle_set_id", vehicle_set_id, "vehicleSet_stats.csv")
        add_info("number_of_vehicles", number_of_vehicles, "vehicleSet_stats.csv")
        add_info("creation_time_laps", duration, "vehicleSet_stats.csv")
        add_info("type", "random", "vehicleSet_stats.csv")

        return vehicle_set_id
    
    @staticmethod
    def create_route_nodes(tx, path, vehicle_node):
        """
        Creates route nodes in the database based on the given path and vehicle node.

        Args:
            path (list): A list of nodes representing the path returned by the A* algorithm.
            vehicle_node: The vehicle node to link with the route nodes.

        Returns:
            None
        """
        vehicle_id = vehicle_node.id
        # Initialize previous node reference
        previous_node_id = None
        # If path is a neo4j.graph.Path, use its .nodes sequence
        nodes = getattr(path, "nodes", path)
        with DatabaseContainer.driver.session() as session:
            # Iterate through the path nodes returned by the A* algorithm
            for i, road_point in enumerate(nodes):
                #print(f"i = {i},\nroad_point = {road_point},\nroad_point.id = {road_point.id}\n")
                # Set default values for departure and waiting_time
                #departure_time = datetime.datetime.now() + datetime.timedelta(minutes=i*5)
                departure_time =datetime.datetime(2024, 1, 1)
                waiting_time = 0
                road_point_id = road_point.id

                # Create the RouteNode
                result = tx.run(
                    "MATCH (rp:RoadPoint) "
                    "WHERE id(rp) = $road_point_id "
                    "CREATE (rn:RouteNode {departure: $departure, waiting_time: $waiting_time})-[:IS_AT]->(rp) "
                    "RETURN id(rn)",
                    road_point_id=road_point_id,
                    departure=departure_time.isoformat(),
                    waiting_time=waiting_time
                )
                current_node_id = result.single()[0]

                # Intermediate nodes: IS_ROUTED_BY
                tx.run(
                    "MATCH (v:Vehicle), (rn:RouteNode) "
                    "WHERE id(v) = $vehicle_id AND id(rn) = $node_id "
                    "CREATE (v)-[:IS_ROUTED_BY]->(rn)",
                    vehicle_id=vehicle_id,
                    node_id=current_node_id
                )

                # Link the vehicle to the RouteNode with :STARTS_AT or :IS_ROUTED_BY
                if i == 0:
                    # First node: STARTS_AT
                    tx.run(
                        "MATCH (v:Vehicle), (rn:RouteNode) "
                        "WHERE id(v) = $vehicle_id AND id(rn) = $node_id "
                        "CREATE (v)-[:STARTS_AT]->(rn)",
                        vehicle_id=vehicle_id,
                        node_id=current_node_id
                    )
                elif i == len(path) - 1:
                    # Last node: ENDS_AT
                    tx.run(
                        "MATCH (v:Vehicle), (rn:RouteNode) "
                        "WHERE id(v) = $vehicle_id AND id(rn) = $node_id "
                        "CREATE (v)-[:ENDS_AT]->(rn)",
                        vehicle_id=vehicle_id,
                        node_id=current_node_id
                    )

                # If there is a previous node, create the NEXT_R relationship
                if previous_node_id is not None:
                    tx.run(
                        "MATCH (prev:RouteNode), (curr:RouteNode) "
                        "WHERE id(prev) = $prev_id AND id(curr) = $curr_id "
                        "CREATE (prev)-[:NEXT_R]->(curr)",
                        prev_id=previous_node_id,
                        curr_id=current_node_id
                    )

                # Update the reference to the previous node
                previous_node_id = current_node_id
                #print(f"Route creator for vehice {vehicle_node.id} created {i+1} of {len(path)} road points at id(RoadPoint) = {road_point.id} osm_id(RoadPoint) = {road_point['osm_id']}")
            logger.info(f"Created {len(path)} :RouteNodes for :Vehicle (<id>={vehicle_node.id}).")
            add_info("total_route_nodes_created", len(path), "vehicle_stats.csv")

    @staticmethod
    def create_random_vehicle_set_trace(number_of_vehicles: int) -> int:
        # doesn't work, the astar throws a ValueError: Values of type <class 'neo4j.graph.Node'> are not supported (Deprecated, Now it works fine😁)
        vehicle_set_id = Database._create_vehicle_set("random", number_of_vehicles)

        with DatabaseContainer.driver.session() as session:
            start_time = datetime.datetime.now()

            # Start a Neo4j transaction
            with session.begin_transaction() as tx:
                # Get the total number of RoadPoints in the graph to pick random points
                road_number = tx.run("MATCH (n:RoadPoint) RETURN COUNT(n) AS road_number").single()[0]
                if road_number < 2:
                    raise ValueError(
                        f"Road network contains insufficient points. Found {road_number} road point(s). "
                        f"At least 2 are required."
                    )

                for _ in range(number_of_vehicles):
                    # Randomly select start and end RoadPoints
                    rnd_1 = random.randint(0, road_number - 1)
                    rnd_2 = random.randint(0, road_number - 1)
                    while rnd_2 == rnd_1:
                        rnd_2 = random.randint(0, road_number - 1)

                    # Find the actual RoadPoints
                    start_time_vehicle = datetime.datetime.now()
                    start_point = tx.run(
                        "MATCH (n:RoadPoint) RETURN n SKIP $rnd_1 LIMIT 1", rnd_1=rnd_1
                    ).single()[0]
                    # print(start_point)

                    end_point = tx.run(
                        "MATCH (n:RoadPoint) RETURN n SKIP $rnd_2 LIMIT 1", rnd_2=rnd_2
                    ).single()[0]

                    # Use IDs (or properties) instead of passing Node objects
                    start_id = start_point.id
                    end_id = end_point.id

                    # Create a new vehicle with a random route between the start and end points
                    vehicle_properties = {
                        "earliest_departure": datetime.datetime.now().isoformat(),
                        "latest_arrival": (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat(),
                        "speed_min": 30,
                        "speed_opt": 60,
                        "speed_max": 90,
                        "technical_requirements": "standard",
                        "legal_requirements": "standard"
                    }
                    
                    # create vehicles with vehicle properties
                    vehicle_node = tx.run(f"""
                            MATCH (vs:{CMD.vehicle_set_label}) WHERE id(vs) = {vehicle_set_id}
                            MATCH (start:RoadPoint), (end:RoadPoint) WHERE id(start) = $start_id AND id(end) = $end_id
                            CREATE (vs)-[:{CMD.vehicle_in_set_rel}]->(v:Vehicle {{properties}})
                            CREATE (v)-[:ORIGIN]->(start)
                            CREATE (v)-[:DESTINATION]->(end)
                            RETURN v
                        """, properties=vehicle_properties, start_id=start_id, end_id=end_id).single()[0]

                    # Calculate the shortest path using the aStar algorithm
                    result = tx.run(
                        """
                        MATCH (start:RoadPoint) WHERE id(start) = $start_id
                        MATCH (end:RoadPoint)   WHERE id(end)   = $end_id
                        CALL apoc.algo.aStar(
                            start,
                            end,
                            'ROAD_SEGMENT',   
                            'distance_meter',
                            'lat',
                            'lon'
                        ) YIELD path, weight
                        RETURN path, weight
                        """,
                        start_id=start_id,
                        end_id=end_id
                    ).single()

                    path = result[0]
                    weight = result['weight']
    
                    end_time_vehicle = datetime.datetime.now()
                    duration_vehicle = (end_time_vehicle - start_time_vehicle).total_seconds()
                    add_info("vehicle_id", vehicle_node.id, "vehicle_stats.csv")
                    add_info("vehicle_creation_time", duration_vehicle, "vehicle_stats.csv")
                    add_info("legal_requirements", vehicle_properties["legal_requirements"], "vehicle_stats.csv")
                    add_info("technical_requirements", vehicle_properties["technical_requirements"], "vehicle_stats.csv")  
                    add_info("average_speed", (vehicle_properties["speed_min"] + vehicle_properties["speed_opt"] + vehicle_properties["speed_max"]) / 3, "vehicle_stats.csv")
                    add_info("earliest_departure", vehicle_properties["earliest_departure"], "vehicle_stats.csv")
                    add_info("latest_arrival", vehicle_properties["latest_arrival"], "vehicle_stats.csv")
                    add_info("vehicle_set_id", vehicle_set_id, "vehicle_stats.csv")
                    # add_info("type", "random", "vehicle_stats.csv")

                    Database.create_route_nodes(tx, path, vehicle_node)

                tx.commit()
                end_time = datetime.datetime.now()
                print("* Created {} vehicle(s) in the set with ID {} in {} seconds.".format(
                    number_of_vehicles, vehicle_set_id, (end_time - start_time).total_seconds()))
                duration = (end_time - start_time).total_seconds()
                add_info("vehicle_set_id", vehicle_set_id, "vehicleSet_stats.csv")
                add_info("number_of_vehicles", number_of_vehicles, "vehicleSet_stats.csv")
                add_info("creation_time_laps", duration, "vehicleSet_stats.csv")
                add_info("type", "random", "vehicleSet_stats.csv")

        return vehicle_set_id
   


    @staticmethod
    def create_depot_vehicle_set(number_of_vehicles: int, min_platooning_distance: int, max_platooning_distance: int) -> int:
        """
        creation of random distributed vehicle for given number of vehicles
        :param number_of_vehicles: number of vehicles
        :param min_platooning_distance: minimum platooning distance of generated vehicles, depends on road network instance
        :param max_platooning_distance: maximum platooning distance of generated vehicles, depends on road network instance
        :return: vehicle set id of created vehicle set
        """

        if min_platooning_distance <= 0:
            raise ValueError("Minimum Platooning Distance is negative or zero: " + str(min_platooning_distance))

        vehicle_set_id = Database._create_vehicle_set("random", number_of_vehicles)

        with DatabaseContainer.driver.session() as session:
            start_time = time.time()

            # Creation of random vehicles
            tx = session.begin_transaction()
            query = "MATCH (vs:" + CMD.vehicle_set_label + ") WHERE id(vs) = " + str(vehicle_set_id) + "\n" \
                    "MATCH (:Depot)-[:LOCATED_AT]->(n1:" + CMD.road_label + ") WITH vs, n1, rand() AS r1 ORDER BY r1 LIMIT " + str(number_of_vehicles) + "\n" \
                    "MATCH (:Depot)-[:LOCATED_AT]->(n2:" + CMD.road_label + ") WHERE distance(point({latitude: n1.lat, longitude: n1.lon}), point({latitude: n2.lat, longitude: n2.lon})) > " + str(min_platooning_distance) + \
                    " AND distance(point({latitude: n1.lat, longitude: n1.lon}), point({latitude: n2.lat, longitude: n2.lon})) <= " + str(max_platooning_distance) + \
                    " WITH vs, n1, n2, rand() AS r2 ORDER BY r2 LIMIT " + str(number_of_vehicles) + "\n" \
                    "CREATE (vs)-[r:" + CMD.vehicle_in_set_rel + "]->(v:" + CMD.vehicle_label + ")\n" \
                    "CREATE (n2)<-[:" + CMD.vehicle_end_rel + "]-(v)-[:" + CMD.vehicle_start_rel + "]->(n1)\n" \
                    "WITH vs, v, n1, n2\n" \
                    "CALL apoc.algo.aStar(n1, n2, \"" + CMD.road_rel + ">\", \"distance_meter\", \"lat\", \"lon\") YIELD path, weight\n" \
                    "WITH vs, v, n1, n2, weight, nodes(path) as path_list, nodes(path)[0] as first, nodes(path)[-1] as last\n" \
                    "FOREACH (pn IN path_list[1..length(path_list)-1] | CREATE (pn)<-[:LOC{ veh_id: id(v)}]-(:RouteNodeTemp))\n" \
                    "CREATE (first)<-[:LOC{ veh_id: id(v)}]-(:RouteNodeTemp)<-[:SP_START]-(v)\n" \
                    "CREATE (last)<-[:LOC{ veh_id: id(v)}]-(:RouteNodeTemp)<-[:SP_END]-(v)\n" \
                    "SET v.shortest_path_distance = weight  WITH v,\n" \
                    "EXTRACT(i IN RANGE(0, LENGTH(path_list) - 2) | [path_list[i], path_list[i+1]]) AS pairs\n" \
                    "UNWIND pairs as pair WITH v, pair[0] as l1, pair[1] as l2, pair WITH v, l1, l2\n" \
                    "MATCH (l1)-[r:" + CMD.road_rel + "]-(l2) MATCH (l1)-[lc1:" + CMD.route_rel + "]-(rn1), (l2)-[lc2:" + CMD.route_rel + "]-(rn2) WHERE lc1.veh_id = id(v) AND lc2.veh_id=id(v)\n" \
                    "CREATE (rn1)-[:" + CMD.next_route_rel + "{distance:r.distance}]->(rn2)"
            tx.run(query)
            
            # Clean up of temp properties
            query = "MATCH ()-[r:" + CMD.route_rel + "]->() REMOVE r.veh_id"
            tx.run(query)
            tx.commit()
            end_time = datetime.datetime.now()
            # Database.check_vehicle_set()
            print("* Created {count} depot vehicle(s) in {time} seconds with id {id}.".format(count=number_of_vehicles,
                                                                          time=round(time.time() - start_time, 2),
                                                                          id=vehicle_set_id))

            duration = (end_time - start_time).total_seconds()

            add_info("vehicle_set_id", vehicle_set_id, "vehicleSet_stats.csv")
            add_info("number_of_vehicles", number_of_vehicles, "vehicleSet_stats.csv")
            add_info("creation_time_laps", duration, "vehicleSet_stats.csv")
            add_info("type", "depot", "vehicleSet_stats.csv")
            return vehicle_set_id


    @staticmethod
    def number_of_vehicles(vehicle_set_id: int):
        with DatabaseContainer.driver.session() as session:
            tx = session.begin_transaction()

            query = "MATCH (vs:" + CMD.vehicle_set_label + ")-[:" + CMD.vehicle_in_set_rel + "]->(vehicle:" + CMD.vehicle_label + "), (end)<-[:END_AT]-(vehicle)-[:START_AT]->(start) WHERE id(vs)=" + str(vehicle_set_id) +" RETURN count(vehicle) as number"

            results = tx.run(query)
            result = results.single()
            tx.commit()

            print("===> Number of vehicles", result.get("number"), "with set id", vehicle_set_id, "are created in Database Neo4j.")

    @staticmethod
    def generate_vehicles(vehicle_set_id: int):
        with DatabaseContainer.driver.session() as session:
            tx = session.begin_transaction()

            query = "MATCH (vs:" + CMD.vehicle_set_label + ")-[:" + CMD.vehicle_in_set_rel + "]->(vehicle:" + CMD.vehicle_label + "), (end)<-[:END_AT]-(vehicle)-[:START_AT]->(start) WHERE id(vs)=" + str(vehicle_set_id) +" RETURN count(vehicle) as number, collect([id(start), id(end)]) as vehicles"

            results = tx.run(query)
            result = results.single()
            tx.commit()

            # text_file = open("config/gen_vehicles", "w")
            # n = text_file.write('Welcome to pythonexamples.org')
            # text_file.close()

            print(result.get("number"))
            print(result.get("vehicles"))

    @staticmethod
    def generate_all_vehicle_sets():
        with DatabaseContainer.driver.session() as session:
            tx = session.begin_transaction()

            query = "MATCH (vs:" + CMD.vehicle_set_label + ")-[:" + CMD.vehicle_in_set_rel + "]->(vehicle:" + CMD.vehicle_label + "), (end)<-[:END_AT]-(vehicle)-[:START_AT]->(start) RETURN id(vs), count(vehicle) as number, collect([id(start), id(end)]) as vehicles"
            print("generate_all_vehicle_sets query = ", query)
            results = tx.run(query)
            if results is None:
                raise ValueError("No vehicle set found in the database.")

            path_to_file = Configuration.exp_path + 'gen_vehicles'
            open(path_to_file, 'w').close()
            i = 0
            text_file = open(path_to_file, "w+")
            for result in results:
                # print(result.get("number"))
                # print(result.get("vehicles"))
                #print("single result #", i, result)
                text_file.write('{ \"test_case_' + str(i) + '\":\n')
                text_file.write(str(result['vehicles']) + "\n}\n")
                i = i + 1

            text_file.close()
            

