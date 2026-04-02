import logging
import time
from typing import Dict, List, Tuple

from util.cmd import CMD
from util.databasecontainer import DatabaseContainer
from util.datautil import DataUtil

# Logging with formatting (to print out the error messages in red)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        raise NotImplementedError("static")

    @staticmethod
    def create_10_10_road_nodes_DEPRECATED():
        with DatabaseContainer.driver.session() as session:
            try:
                create_query = ('''
                WITH 50.0*1000 AS width,
                    50.0*1000 AS height, 
                    10 AS x_num, 
                    10 AS y_num, 
                    10 AS depot_num 
                UNWIND range(0, x_num-1) AS x 
                UNWIND range(0, y_num-1) AS y 

                WITH *, x * width / 110574.0 AS lat 

                WITH *, y * height / (111320.0 * cos(lat/360.0)) AS lon 

                CREATE (n:RoadPoint {lat: lat, lon: lon, x: x, y: y}) 

                WITH DISTINCT x_num, y_num, depot_num 
                UNWIND range(0, x_num-1) AS x 
                UNWIND range(0, y_num-2) AS y 

                MATCH (n:RoadPoint) WHERE n.x = x AND n.y = y 
                MATCH (m:RoadPoint) WHERE m.x = x AND m.y = y+1 

                WITH *, point.distance(point({latitude: n.lat, longitude: n.lon}), point({latitude: m.lat, longitude: m.lon})) AS d 

                CREATE (n)-[:ROAD_SEGMENT {distance_meter: d, distance: d/1000.0}]->(m)<-[:ROAD_SEGMENT {distance_meter: d, distance: d/1000.0}]-(n) 

                WITH DISTINCT x_num, y_num, depot_num 
                UNWIND range(0, x_num-2) AS x 
                UNWIND range(0, y_num-1) AS y 

                MATCH (n:RoadPoint) WHERE n.x = x AND n.y = y 
                MATCH (m:RoadPoint) WHERE m.x = x+1 AND m.y = y 

                WITH *, point.distance(point({latitude: n.lat, longitude: n.lon}), point({latitude: m.lat, longitude: m.lon})) AS d 

                CREATE (n)-[:ROAD_SEGMENT {distance_meter: d, distance: d/1000.0}]->(m)-[:ROAD_SEGMENT {distance_meter: d, distance: d/1000.0}]->(n) 

                WITH DISTINCT depot_num 
                MATCH (n:RoadPoint) 

                WITH depot_num, n, rand() AS r 
                ORDER BY r DESC 

                WITH COLLECT(n) AS depot_roads 
                UNWIND depot_roads AS depot_road 

                CREATE (:Depot)-[:LOCATED_AT]->(depot_road)
                '''
                                )
                print("executing create_10_10_road_nodes query.")
                session.run(create_query)
                print("create_10_10_road_nodes query executed.")
            except Exception as e:
                print(f"An error occurred during execution of the following query \n{create_query} \nException: {e}")

        with DatabaseContainer.driver.session() as session:
            try:
                # Parameters setup
                params_setup = '''
                WITH 50.0 * 1000 AS width, 50.0 * 1000 AS height, 
                    10 AS x_num, 10 AS y_num, 10 AS depot_num
                '''

                # Generate RoadPoint nodes
                generate_road_points = '''
                UNWIND range(0, x_num - 1) AS x
                UNWIND range(0, y_num - 1) AS y
                WITH *, x * width / 110574 AS lat, 
                    y * height / (111320 * cos(lat / 360 * pi())) AS lon
                CREATE (n:RoadPoint {lat: lat, lon: lon, x: x, y: y})
                '''

                # Connect RoadPoints horizontally
                connect_horizontal = '''
                WITH x_num, y_num
                UNWIND range(0, x_num - 1) AS x
                UNWIND range(0, y_num - 2) AS y
                MATCH (n:RoadPoint {x: x, y: y})
                MATCH (m:RoadPoint {x: x, y: y + 1})
                CREATE (n)-[:ROAD_SEGMENT]->(m)
                CREATE (m)-[:ROAD_SEGMENT]->(n)
                '''

                # Connect RoadPoints vertically
                connect_vertical = '''
                WITH x_num, y_num
                UNWIND range(0, x_num - 2) AS x
                UNWIND range(0, y_num - 1) AS y
                MATCH (n:RoadPoint {x: x, y: y})
                MATCH (m:RoadPoint {x: x + 1, y: y})
                CREATE (n)-[:ROAD_SEGMENT]->(m)
                CREATE (m)-[:ROAD_SEGMENT]->(n)
                '''

                place_depots = '''
                WITH depot_num
                MATCH (n:RoadPoint)
                WITH n, rand() AS r, depot_num ORDER BY r DESC
                WITH COLLECT(n) AS nodes, depot_num
                WITH nodes[0..depot_num] AS selected_depots
                UNWIND selected_depots AS depot_road
                CREATE (:Depot)-[:LOCATED_AT]->(depot_road)
                '''

                # Combine all parts into one query
                create_query = (
                        params_setup +
                        generate_road_points +
                        connect_horizontal +
                        connect_vertical +
                        place_depots
                )

                print("Executing create_10_10_road_nodes query.")
                session.run(create_query)
                print("create_10_10_road_nodes query executed.")
            except Exception as e:
                print(f"An error occurred during execution: {e}")

    @staticmethod
    def create_10_10_road_nodes():
        with DatabaseContainer.driver.session() as session:
            try:
                # Defining the parameters and initial nodes creation
                initial_setup = '''
                WITH 50.0*1000 AS width,
                    50.0*1000 AS height, 
                    10 AS x_num, 
                    10 AS y_num, 
                    10 AS depot_num 
                UNWIND range(0, x_num-1) AS x 
                UNWIND range(0, y_num-1) AS y 
                WITH *, x * width / 110574.0 AS lat 
                WITH *, y * height / (111320.0 * cos(lat/360.0)) AS lon 
                CREATE (n:RoadPoint {lat: lat, lon: lon, x: x, y: y}) 
                '''

                # Creating vertical road segments
                vertical_roads_creation = '''
                WITH DISTINCT x_num, y_num, depot_num 
                UNWIND range(0, x_num-1) AS x 
                UNWIND range(0, y_num-2) AS y 
                MATCH (n:RoadPoint) WHERE n.x = x AND n.y = y 
                MATCH (m:RoadPoint) WHERE m.x = x AND m.y = y+1 
                WITH *, point.distance(point({latitude: n.lat, longitude: n.lon}), point({latitude: m.lat, longitude: m.lon})) AS d 
                CREATE (n)-[:ROAD_SEGMENT {distance_meter: d, distance: d/1000.0, lanes: 4, speed_limits: 100}]->(m)
                CREATE (m)-[:ROAD_SEGMENT {distance_meter: d, distance: d/1000.0, lanes: 4, speed_limits: 100}]->(n)

                '''

                # Creating horizontal road segments
                horizontal_roads_creation = '''
                WITH DISTINCT x_num, y_num, depot_num 
                UNWIND range(0, x_num-2) AS x 
                UNWIND range(0, y_num-1) AS y 
                MATCH (n:RoadPoint) WHERE n.x = x AND n.y = y 
                MATCH (m:RoadPoint) WHERE m.x = x+1 AND m.y = y 
                WITH *, point.distance(point({latitude: n.lat, longitude: n.lon}), point({latitude: m.lat, longitude: m.lon})) AS d 
                CREATE (n)-[:ROAD_SEGMENT {distance_meter: d, distance: d/1000.0, lanes: 4, speed_limits: 100}]->(m)
                CREATE (m)-[:ROAD_SEGMENT {distance_meter: d, distance: d/1000.0, lanes: 4, speed_limits: 100}]->(n)
                '''

                # Creating depots
                depots_creation = '''
                WITH DISTINCT depot_num 
                MATCH (n:RoadPoint) 
                WITH depot_num, n, rand() AS r 
                ORDER BY r DESC 
                WITH COLLECT(n) AS depot_roads 
                UNWIND depot_roads AS depot_road 
                CREATE (:Depot)-[:LOCATED_AT]->(depot_road)
                '''

                # Combining all parts into one query
                create_query = initial_setup + vertical_roads_creation + horizontal_roads_creation  # + depots_creation

                print("executing create_10_10_road_nodes query.")
                session.run(create_query)
                print("create_10_10_road_nodes query executed.")
            except Exception as e:
                print(f"An error occurred during execution of the following query \n{create_query} \nException: {e}")

    @staticmethod
    def get_road_network_meta_data() -> Dict:
        try:
            with DatabaseContainer.driver.session() as session:
                query = "MATCH ()-[r:" + CMD.road_rel + "]->() WITH count(r) as number_of_edges MATCH (l:" + CMD.road_label + ") " \
                                                                                                                              "RETURN count(l) AS number_of_road_points, number_of_edges, avg(apoc.node.degree(l,'" + CMD.road_rel + "')) as avg_road_point_degree"
                results = session.run(query)
                # print ("get_road_network_meta_data query = ", query)
                result = results.single()
                return result
        except Exception as e:
            # ANSI escape code for red text within logging
            red_text = "\033[91m"
            reset_text = "\033[0m"
            logger.error(red_text + "\n\n" + "*" * 60 +
                         "\nERROR WHILE LOADING ROAD NETWORK METADATA: FAILED TO ESTABLISH A SESSION WITH NEO4J DATABASE\n"
                         "POSSIBLE CAUSES: Docker container not running, network issues, or Neo4j driver problem.\n"
                         f"EXCEPTION DETAILS: {e}\n" + "*" * 60 + reset_text + "\n")
            exit

    @staticmethod
    def get_number_of_road_nodes() -> int:
        with DatabaseContainer.driver.session() as session:
            query = "MATCH (n: " + CMD.road_label + ") RETURN count(n) as number_of_road_nodes"
            results = session.run(query)
            result = results.single()
            number_of_road_nodes = result.get("number_of_road_nodes")
            return number_of_road_nodes

    @staticmethod
    def get_number_of_vehicles(vehicle_set_id: int) -> int:
        with DatabaseContainer.driver.session() as session:
            query = "MATCH (vs: VehicleSet)-[: CONSISTS_OF]->(n:" + CMD.vehicle_label + ") WHERE id(vs) = " + str(
                vehicle_set_id) + " RETURN count(n) as number_of_vehicles"
            results = session.run(query)
            result = results.single()
            number_of_vehicles = result.get("number_of_vehicles")
            return number_of_vehicles

    @staticmethod
    def get_vehicles_shortest_path_by_set_id(vehicle_set_id: int) -> List[Tuple]:
        with DatabaseContainer.driver.session() as session:
            query = "MATCH (vs:" + CMD.vehicle_set_label + ")-[:" + CMD.vehicle_in_set_rel + "]->(v:" + CMD.vehicle_label + ") WHERE id(vs) = " + str(
                vehicle_set_id) + " WITH v " \
                                  "MATCH (end:" + CMD.road_label + ")<-[r2:" + CMD.vehicle_end_rel + "]-(v)-[r1:" + CMD.vehicle_start_rel + "]->(start:" + CMD.road_label + ") " \
                                                                                                                                                                            "WITH v, start, end CALL apoc.algo.aStar(start, end, '" + CMD.road_rel + ">', 'distance_meter','lat','lon')  YIELD weight, path RETURN id(v) AS vehicle_id, weight, path"
            results = session.run(query)

            vehicle_paths = []
            for result in results:
                vehicle_paths.append(DataUtil.create_path_from_result_with_vehicle_id(result))

            return vehicle_paths

    @staticmethod
    def remove_unconnected_road_nodes() -> None:
        with DatabaseContainer.driver.session() as session:
            print("\n- Remove unconnected road nodes. -")
            start_time = time.time()
            tx = session.begin_transaction()

            number_of_nodes = Database.get_number_of_road_nodes()
            number_of_removed_nodes = 0

            # query = "CALL algo.unionFind.stream('" + CMD.road_label + "', '" + CMD.road_rel + "', {}) " \ #this was renamed into gds.wcc.write
            query = "CALL gds.wcc.write('" + CMD.road_label + "', '" + CMD.road_rel + "', {}) " \
                                                                                      "YIELD nodeId,setId WITH COUNT(nodeId) AS n, setId " \
                                                                                      "RETURN COUNT(setId) AS number"
            results = tx.run(query)
            result = results.single()
            connected_component_number = result.get("number")

            print(" There are {number} connected components.".format(number=connected_component_number))

            if connected_component_number > 1:
                # query = "CALL algo.unionFind.stream('" + CMD.road_label + "', '" + CMD.road_rel + "', {}) " \ #this was renamed into gds.wcc.write
                query = "CALL gds.wcc.write('" + CMD.road_label + "', '" + CMD.road_rel + "', {}) " \
                                                                                          "YIELD nodeId, setId " \
                                                                                          "MATCH (n:" + CMD.road_label + ") " \
                                                                                                                         "WHERE ID(n) = nodeId " \
                                                                                                                         "SET n.partition = setId"
                tx.run(query)
                query = "MATCH (n:" + CMD.road_label + ") WITH COUNT(n) AS c, n.partition AS s " \
                                                       "ORDER BY c DESC LIMIT 1 " \
                                                       "MATCH (n:" + CMD.road_label + ") WHERE n.partition <> s " \
                                                                                      "DETACH DELETE n RETURN COUNT(n) AS number"
                for result in tx.run(query):
                    number_of_removed_nodes = result.get("number")
                query = "MATCH (n:" + CMD.road_label + ") REMOVE n.partition"
                tx.run(query)

            tx.commit()
            print("Removed {removed_nodes} nodes out of {total_nodes} nodes ({remaining_nodes} nodes left) "
                  "in {time} seconds.".format(removed_nodes=number_of_removed_nodes, total_nodes=number_of_nodes,
                                              remaining_nodes=number_of_nodes - number_of_removed_nodes,
                                              time=round(time.time() - start_time, 2)))

    @staticmethod
    def clean_up():
        start_time = time.time()
        Database.clean_up_filters()
        Database.clean_up_routes()
        Database.clean_up_groups()
        Database.clean_up_platoons()
        Database.clean_up_incentives()
        Database.clean_up_vehicle_sets_vehicles()
        print("* Entire data set cleaned up in {time} seconds.".format(time=round(time.time() - start_time, 2)))

    @staticmethod
    def clean_up_routes(time_log: bool = False):
        with DatabaseContainer.driver.session() as session:
            start_time = time.time()
            query = 'Call apoc.periodic.iterate("MATCH (v:' + CMD.route_label + ') return v", "detach delete v", {batchSize:10000});'
            session.run(query)
            if time_log:
                print("* Route data set cleaned up in {time} seconds.".format(time=round(time.time() - start_time, 2)))

    @staticmethod
    def clean_up_filters(time_log: bool = False):
        with DatabaseContainer.driver.session() as session:
            start_time = time.time()
            query = 'Call apoc.periodic.iterate("MATCH (v:' + CMD.location_label + ') return v", "detach delete v", {batchSize:10000});'
            # print("Running query:\n" + query + "\n")
            session.run(query)
            if time_log:
                print("* Filter data set cleaned up in {time} seconds.".format(time=round(time.time() - start_time, 2)))

    @staticmethod
    def clean_up_groups(time_log: bool = False):
        with DatabaseContainer.driver.session() as session:
            start_time = time.time()
            query = 'Call apoc.periodic.iterate("MATCH (v:' + CMD.group_label + ') return v", "detach delete v", {batchSize:10000});'
            session.run(query)
            if time_log:
                print("* Group data set cleaned up in {time} seconds.".format(time=round(time.time() - start_time, 2)))

    @staticmethod
    def clean_up_platoons(time_log: bool = False):
        with DatabaseContainer.driver.session() as session:
            start_time = time.time()
            query = 'Call apoc.periodic.iterate("MATCH (v:' + CMD.platoon_route_node_label + ') return v", "detach delete v", {batchSize:10000});'
            session.run(query)

            query = 'Call apoc.periodic.iterate("MATCH (v:' + CMD.platoon_route_label + ') return v", "detach delete v", {batchSize:10000});'
            session.run(query)

            query = 'Call apoc.periodic.iterate("MATCH (v:' + CMD.platoon_via_label + ') return v", "detach delete v", {batchSize:10000});'
            session.run(query)

            if time_log:
                print(
                    "* Platoon data set cleaned up in {time} seconds.".format(time=round(time.time() - start_time, 2)))

    @staticmethod
    def clean_up_incentives(time_log: bool = False):
        with DatabaseContainer.driver.session() as session:
            start_time = time.time()
            query = 'Call apoc.periodic.iterate("MATCH (v:' + CMD.inactive_incentive_label + ') return v", "detach delete v", {batchSize:10000});'
            session.run(query)

            query = 'Call apoc.periodic.iterate("MATCH (v:' + CMD.inactive_label + ') return v", "detach delete v", {batchSize:10000});'
            session.run(query)

            query = 'Call apoc.periodic.iterate("MATCH (v:' + CMD.incentive_label + ') return v", "detach delete v", {batchSize:10000});'
            session.run(query)

            if time_log:
                print("* Incentive data set cleaned up in {time} seconds.".format(
                    time=round(time.time() - start_time, 2)))

    @staticmethod
    def clean_up_vehicle_sets_vehicles(time_log: bool = False):
        with DatabaseContainer.driver.session() as session:
            start_time = time.time()
            query = 'Call apoc.periodic.iterate("MATCH (v:' + CMD.vehicle_label + ') return v", "detach delete v", {batchSize:10000});'
            session.run(query)

            query = 'Call apoc.periodic.iterate("MATCH (v:' + CMD.vehicle_set_label + ') return v", "detach delete v", {batchSize:10000});'
            session.run(query)

            if time_log:
                print(
                    "* Platoon data set cleaned up in {time} seconds.".format(time=round(time.time() - start_time, 2)))

    @staticmethod
    def clean_up_groups_by_vehicle_set(vehicle_set: int):
        # ToDo Incentive should be cleaned?
        with DatabaseContainer.driver.session() as session:
            query = "MATCH (vs:" + CMD.vehicle_set_label + ")-[r:" + CMD.vehicle_in_set_rel + "]->(v:" + CMD.vehicle_label + ")-[:" + CMD.in_group_rel + "]->(g:" + CMD.group_label + ") WHERE id(vs)=" + str(
                vehicle_set) + " DETACH DELETE g"
            session.run(query)

    @staticmethod
    # return the total number of RoadPoints in the database
    def count_road_points() -> int:
        with DatabaseContainer.driver.session() as session:
            query = "MATCH (n:" + CMD.road_label + ") RETURN count(n) AS number_of_road_points"
            results = session.run(query)
            result = results.single()
            number_of_road_points = result.get("number_of_road_points")
            return number_of_road_points
        
    # return the total number of RoadSegments in the database
    @staticmethod
    def count_road_segments() -> int:
        with DatabaseContainer.driver.session() as session:
            query = "MATCH ()-[r:" + CMD.road_rel + "]->() RETURN count(r) AS number_of_road_segments"
            results = session.run(query)
            result = results.single()
            number_of_road_segments = result.get("number_of_road_segments")
            return number_of_road_segments
