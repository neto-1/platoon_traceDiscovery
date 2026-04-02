import configparser
import os.path
import sys
from neo4j.v1 import GraphDatabase, Session
from typing import List, Tuple
import csv


class Configuration:
    _filename = 'config.ini'

    def __init__(self) -> None:
        self._config = configparser.ConfigParser()
        if not os.path.isfile(self._filename):
            self.set_default()
        self._config.read(self._filename)

    def set_default(self) -> None:
        self._config['importer'] = {
            'road_point_label': 'Road',
            'road_segment_name': 'neighbour'
        }
        self._config['config'] = {
            'host': 'localhost',
            'bolt_port': 7687,
            'user': 'neo4j',
            'password': '12345678',
            'road_point_label': 'RoadPoint',
            'road_segment_name': 'ROAD_SEGMENT',
            'poi_label': 'Depot',
            'poi_mapping_radius_km': 5
        }
        self._write()

    def _write(self):
        with open(self._filename, 'w') as configfile:
            self._config.write(configfile)

    def set(self, option: str, value: str or int) -> None:
        self._config.set('config', option, value)
        self._write()

    def get(self, option: str) -> str or int:
        return self._config.get('config', option)

    def get_importer(self, option: str) -> str:
        return self._config.get('importer', option)


class PointsOfInterest:
    def __init__(self, poi_list: List[Tuple[float, float]]) -> None:
        self._poi_list = poi_list

    def get_poi_list(self) -> List[Tuple[float, float]]:
        return self._poi_list

    @classmethod
    def _cast_float(cls, unspecific_float: str) -> float:
        if unspecific_float.count(".") + unspecific_float.count(",") > 1:
            raise ValueError('Please do not use thousands separators.')
        if ',' in unspecific_float:
            unspecific_float = unspecific_float.replace(',', '.')
        return float(unspecific_float)

    @classmethod
    def read_from_csv(cls, filename) -> object:
        with open(filename, "rt", encoding="utf-8-sig") as file:
            reader = csv.reader(file, delimiter=';')
            found_header = False
            poi_list = []
            for row in reader:
                if not found_header:
                    if row[0] == "Longitude" and row[1] == "Latitude":
                        found_header = True
                    else:
                        print(" ### ERROR: Found no suitable poi header in csv file", filename, "### ")
                else:
                    longitude = cls._cast_float(row[0])
                    latitude = cls._cast_float(row[1])
                    # longitude > 0 and Negative values for longitude are possible
                    if latitude > 0:
                        coordinates = (longitude, latitude)
                        poi_list.append(coordinates)
            return cls(poi_list)


class Database:
    def __init__(self, config: Configuration) -> None:
        self._driver = GraphDatabase.driver("bolt://" + config.get('host') + ":" + config.get('bolt_port'), auth=(config.get('user'), config.get('password')), max_connection_lifetime=7200)
        self._importer_road_point_label = config.get_importer('road_point_label')
        self._importer_road_segment_name = config.get_importer('road_segment_name')
        self._road_point_label = config.get('road_point_label')
        self._road_segment_name = config.get('road_segment_name')
        self._poi_label = config.get('poi_label')
        self._poi_mapping_radius_km = config.get('poi_mapping_radius_km')

    def get_importer_road_point_number(self) -> int:
        with self._driver.session() as session:
            query = "MATCH (n:{road_point}) " \
                    "RETURN count(n) AS number" \
                    "".format(road_point=self._importer_road_point_label)
            results = session.run(query)
            result = results.single()
            return result.get("number")

    def get_importer_road_segment_number(self) -> int:
        with self._driver.session() as session:
            query = "MATCH ()-[r:{road_segment}]->() " \
                    "RETURN count(r) AS number" \
                    "".format(road_segment=self._importer_road_segment_name)
            results = session.run(query)
            result = results.single()
            return result.get("number")

    def get_road_point_number(self) -> int:
        with self._driver.session() as session:
            query = "MATCH (n:{road_point}) " \
                    "RETURN count(n) AS number" \
                    "".format(road_point=self._road_point_label)
            results = session.run(query)
            result = results.single()
            return result.get("number")

    def get_road_segment_number(self) -> int:
        with self._driver.session() as session:
            query = "MATCH ()-[r:{road_segment}]->() " \
                    "RETURN count(r) AS number" \
                    "".format(road_segment=self._road_segment_name)
            results = session.run(query)
            result = results.single()
            return result.get("number")

    def get_road_segment_number_for_type(self, road_type: str) -> int:
        with self._driver.session() as session:
            query = "MATCH (:{road_type})-[r]->({road_type}) " \
                    "RETURN count(r) AS number" \
                    "".format(road_type=road_type)
            results = session.run(query)
            result = results.single()
            return result.get("number")

    def get_spatial_layers(self) -> list:
        with self._driver.session() as session:
            query = "CALL spatial.layers()"
            results = session.run(query)
            layers = []
            for result in results:
                layer_name = result.get("name")
                layer_signature = result.get("signature")
                layers.append((layer_name, layer_signature))

        return layers


    def is_label_transformed(self) -> bool:
        importer_road_point_number = self.get_importer_road_point_number()
        road_point_number = self.get_road_point_number()
        importer_road_segment_number = self.get_importer_road_segment_number()
        road_segment_number = self.get_road_segment_number()
        return importer_road_point_number + importer_road_segment_number == 0

    def transform_labels(self) -> Tuple[int, int]:
        with self._driver.session() as session:
            # transform road points
            query = "CALL apoc.periodic.commit('" \
                    "MATCH (n:{importer_road_point}) " \
                    "WITH * LIMIT 10000 " \
                    "SET n:{road_point} " \
                    "REMOVE n:{importer_road_point} " \
                    "RETURN count(n) AS number" \
                    "', {{limit:1}}) " \
                    "YIELD updates, executions " \
                    "RETURN updates" \
                    "".format(importer_road_point=self._importer_road_point_label, road_point=self._road_point_label)
            results = session.run(query)
            result = results.single()
            transformed_road_points = result.get("updates")
            # transform road segments
            query = "CALL apoc.periodic.commit('" \
                    "MATCH (n:{road_point})-[r1:{importer_road_segment}]->(m:{road_point}) " \
                    "WITH * LIMIT 10000 " \
                    "CREATE (n)-[r2:{road_segment}]->(m) " \
                    "SET r2.distance_meter = distance(point({{longitude: n.lon, latitude: n.lat}}), point({{longitude: m.lon, latitude: m.lat}})) " \
                    "SET r2.distance = r2.distance_meter/1000 " \
                    "DELETE r1 " \
                    "RETURN count(n) AS number" \
                    "', {{limit:1}}) " \
                    "YIELD updates, executions " \
                    "RETURN updates" \
                    "".format(road_point=self._road_point_label, importer_road_segment=self._importer_road_segment_name, road_segment=self._road_segment_name)
            results = session.run(query)
            result = results.single()
            transformed_road_segments = result.get("updates")
            # return the number of affected nodes and relationships
            return transformed_road_points, transformed_road_segments

    def get_weakly_unconnected_components_number(self) -> Tuple[int, int]:
        with self._driver.session() as session:
            query = "CALL algo.unionFind.stream('{road_point}', '{road_segment}', {{}}) " \
                    "YIELD nodeId, setId " \
                    "WITH COUNT(nodeId) AS n, setId ORDER BY n DESC SKIP 1 " \
                    "RETURN COUNT(setId) AS components, SUM(n) AS nodes" \
                    "".format(road_point=self._road_point_label, road_segment=self._road_segment_name)
            results = session.run(query)
            result = results.single()
            return result.get("components"), result.get("nodes")

    def is_weakly_connected(self) -> bool:
        return self.get_weakly_unconnected_components_number()[0] == 0

    def delete_weakly_unconnected_components(self) -> None:
        with self._driver.session() as session:
            query = "CALL algo.unionFind.stream('{road_point}', '{road_segment}', {{}}) YIELD nodeId, setId " \
                    "MATCH (n:{road_point}) WHERE ID(n) = nodeId SET n.partition = setId" \
                    "".format(road_point=self._road_point_label, road_segment=self._road_segment_name)
            session.run(query)
            query = "CALL apoc.periodic.commit('" \
                    "MATCH (n:{road_point}) WITH COUNT(n) AS c, n.partition AS s ORDER BY c DESC LIMIT 1 " \
                    "MATCH (n:{road_point}) WHERE n.partition <> s " \
                    "WITH * LIMIT 100000 " \
                    "DETACH DELETE n " \
                    "RETURN COUNT(*)" \
                    "', {{limit:1}}) " \
                    "YIELD updates, executions " \
                    "RETURN updates" \
                    "".format(road_point=self._road_point_label)
            session.run(query)
            query = "MATCH (n:{road_point}) REMOVE n.partition" \
                    "".format(road_point=self._road_point_label)
            session.run(query)

    def is_directed_graph(self) -> bool:
        with self._driver.session() as session:
            query = "MATCH (n:{road_point})-[r:{road_segment}]->(m:{road_point}) " \
                    "WHERE (m)-[:{road_segment}]->(n) " \
                    "RETURN count(r) AS number" \
                    "".format(road_point=self._road_point_label, road_segment=self._road_segment_name)
            results = session.run(query)
            result = results.single()
            return result.get("number") > 0

    def insert_reverse_edges(self) -> int:
        with self._driver.session() as session:
            query = "MATCH (n:primary)-[r1:{road_segment}]->(m:primary) " \
                    "WHERE NOT (m)-[:{road_segment}]->(n) " \
                    "CREATE (m)-[r2:{road_segment}]->(n) " \
                    "SET r2.distance = r1.distance " \
                    "SET r2.distance_meter = r1.distance_meter " \
                    "RETURN count(r2) AS number" \
                    "".format(road_segment=self._road_segment_name)
            results = session.run(query)
            result = results.single()
            return result.get("number")

    def get_strongly_unconnected_components_number(self) -> Tuple[int, int]:
        with self._driver.session() as session:
            query = "CALL algo.scc.stream('{road_point}', '{road_segment}', {{}}) " \
                    "YIELD nodeId, partition " \
                    "WITH COUNT(nodeId) AS n, partition ORDER BY n DESC SKIP 1 " \
                    "RETURN COUNT(partition) AS components, SUM(n) AS nodes" \
                    "".format(road_point=self._road_point_label, road_segment=self._road_segment_name)
            results = session.run(query)
            result = results.single()
            return result.get("components"), result.get("nodes")

    def is_strongly_connected(self) -> bool:
        return self.get_strongly_unconnected_components_number()[0] == 0

    def delete_strongly_unconnected_components(self) -> None:
        with self._driver.session() as session:
            query = "CALL algo.scc.stream('{road_point}', '{road_segment}', {{}}) YIELD nodeId, partition " \
                    "MATCH (n:{road_point}) WHERE ID(n) = nodeId SET n.partition = partition" \
                    "".format(road_point=self._road_point_label, road_segment=self._road_segment_name)
            session.run(query)
            query = "CALL apoc.periodic.commit('" \
                    "MATCH (n:{road_point}) WITH COUNT(n) AS c, n.partition AS s ORDER BY c DESC LIMIT 1 " \
                    "MATCH (n:{road_point}) WHERE n.partition <> s " \
                    "WITH * LIMIT 100000 " \
                    "DETACH DELETE n " \
                    "RETURN COUNT(*)" \
                    "', {{limit:1}}) " \
                    "YIELD updates, executions " \
                    "RETURN updates" \
                    "".format(road_point=self._road_point_label)
            session.run(query)
            query = "MATCH (n:{road_point}) REMOVE n.partition" \
                    "".format(road_point=self._road_point_label)
            session.run(query)

    def exist_pois(self) -> bool:
        with self._driver.session() as session:
            query = "MATCH (poi:{poi_label}) RETURN COUNT(poi) AS number" \
                    "".format(poi_label=self._poi_label)
            results = session.run(query)
            result = results.single()
            pois_number = result.get("number")
            return pois_number > 0

    def insert_pois(self, poi_list: List[Tuple[float, float]]) -> int:
        with self._driver.session() as session:
            # check if a layer exists
            query = "CALL spatial.layers() YIELD name WITH name WHERE name = 'roadgeohash' RETURN COUNT(name) AS number"
            results = session.run(query)
            result = results.single()
            layer_number = result.get("number")
            if layer_number == 0:
                # create a layer
                query = "CALL spatial.addPointLayerWithConfig('roadgeohash','lon:lat','geohash')"
                results = session.run(query)
                # populate the layer
                current = 0
                step = 100000
                count = step
                while count == step:
                    query = "MATCH (n:{road_point}) " \
                            "WITH n SKIP {skip} LIMIT {limit} " \
                            "WITH COLLECT(n) AS m CALL spatial.addNodes('roadgeohash', m) YIELD count " \
                            "RETURN count" \
                            "".format(road_point=self._road_point_label, skip=current, limit=step)
                    results = session.run(query)
                    result = results.single()
                    count = result.get("count")
                    current += count
            # add pois
            added_pois_number = 0
            for coordinates in poi_list:
                query = "CALL spatial.withinDistance('roadrtree', {{lon: {lon}, lat: {lat}}}, {radius_kilometer}) YIELD node AS road_list, distance " \
                        "WITH COLLECT(road_list) AS road_list WHERE SIZE(road_list) > 0 " \
                        "WITH road_list[0] AS road_point " \
                        "CREATE (poi:{poi_label} {{lon: {lon}, lat: {lat}}})-[:LOCATED_AT]->(road_point) " \
                        "RETURN COUNT(*) AS number" \
                        "".format(poi_label=self._poi_label, lon=coordinates[0], lat=coordinates[1], radius_kilometer=self._poi_mapping_radius_km)
                results = session.run(query)
                result = results.single()
                added_pois_number += result.get("number")
            return added_pois_number

    def delete_road_points_with_degree_one(self) -> int:
        with self._driver.session() as session:
            query = "CALL apoc.periodic.commit('" \
                    "MATCH (n:{road_point})-[:{road_segment}]-(m:{road_point}) " \
                    "WHERE NOT (:{poi_label})-[:LOCATED_AT]->(n) " \
                    "WITH n, COUNT(DISTINCT m) AS c " \
                    "WHERE c <= 1 " \
                    "DETACH DELETE n " \
                    "RETURN COUNT(*)" \
                    "', {{limit:1}}) " \
                    "YIELD updates, executions " \
                    "RETURN updates" \
                    "".format(poi_label=self._poi_label, road_point=self._road_point_label, road_segment=self._road_segment_name)
            results = session.run(query)
            result = results.single()
            return result.get("updates")

    def delete_road_points_with_degree_two(self) -> int:
        with self._driver.session() as session:
            deleted_nodes_number = 0
            road_point_types = ["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link"]
            for road_point_type in road_point_types:
                query = "CALL apoc.periodic.commit('" \
                        "MATCH (n1:{road_point_type})-[r1:{road_segment}]->(n2:{road_point_type})-[r2:{road_segment}]->(n3:{road_point_type}) " \
                        "WHERE NOT (:{poi_label})-[:LOCATED_AT]->(n2) " \
                        "AND size((n1)-[:{road_segment}]-()) > 2 AND size((n2)-[:{road_segment}]-()) = 2 " \
                        "AND n1 <> n3 " \
                        "CREATE (n1)-[r:{road_segment} {{distance: r1.distance+r2.distance, distance_meter: r1.distance_meter+r2.distance_meter}}]->(n3) " \
                        "DETACH DELETE n2 " \
                        "RETURN COUNT(*)" \
                        "', {{limit:1}}) " \
                        "YIELD updates, executions " \
                        "RETURN updates" \
                        "".format(poi_label=self._poi_label, road_point_type=road_point_type, road_point=self._road_point_label, road_segment=self._road_segment_name)
                results = session.run(query)
                result = results.single()
                deleted_nodes_number += result.get("updates")
                query = "CALL apoc.periodic.commit('" \
                        "MATCH (n1:{road_point_type})-[r1:{road_segment}]->(n2:{road_point_type})-[r2:{road_segment}]->(n3:{road_point_type}) " \
                        "WHERE NOT (:{poi_label})-[:LOCATED_AT]->(n2) " \
                        "AND size((n2)-[:{road_segment}]-()) = 2 " \
                        "AND n1 <> n3 " \
                        "WITH * LIMIT 1 " \
                        "CREATE (n1)-[r:{road_segment} {{distance: r1.distance+r2.distance, distance_meter: r1.distance_meter+r2.distance_meter}}]->(n3) " \
                        "DETACH DELETE n2 " \
                        "RETURN COUNT(*)" \
                        "', {{limit:1}}) " \
                        "YIELD updates, executions " \
                        "RETURN updates" \
                        "".format(poi_label=self._poi_label, road_point_type=road_point_type, road_point=self._road_point_label, road_segment=self._road_segment_name)
                results = session.run(query)
                result = results.single()
                deleted_nodes_number += result.get("updates")
            return deleted_nodes_number

    def delete_road_points_with_degree_four(self) -> int:
        with self._driver.session() as session:
            deleted_nodes_number = 0
            road_point_types = ["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link"]
            for road_point_type in road_point_types:
                query = "CALL apoc.periodic.commit('" \
                        "MATCH (n1:{road_point_type})-[r1:{road_segment}]->(n2:{road_point_type})-[r2:{road_segment}]->(n3:{road_point_type}) " \
                        "WHERE NOT (:{poi_label})-[:LOCATED_AT]->(n2) " \
                        "AND size((n1)-[:{road_segment}]-()) > 4 AND size((n2)-[:{road_segment}]-()) = 4 AND size((n3)-[:{road_segment}]-()) = 4 " \
                        "AND n1 <> n3 " \
                        "MATCH (n3)-[r3:{road_segment}]->(n2)-[r4:{road_segment}]->(n1) " \
                        "CREATE (n1)-[rr1:{road_segment} {{distance: r1.distance+r2.distance, distance_meter: r1.distance_meter+r2.distance_meter}}]->(n3) " \
                        "CREATE (n3)-[rr2:{road_segment} {{distance: r3.distance+r4.distance, distance_meter: r3.distance_meter+r4.distance_meter}}]->(n1) " \
                        "DETACH DELETE n2 " \
                        "RETURN COUNT(*)" \
                        "', {{limit:1}}) " \
                        "YIELD updates, executions " \
                        "RETURN updates" \
                        "".format(poi_label=self._poi_label, road_point_type=road_point_type, road_point=self._road_point_label, road_segment=self._road_segment_name)
                results = session.run(query)
                result = results.single()
                deleted_nodes_number += result.get("updates")
                query = "CALL apoc.periodic.commit('" \
                        "MATCH (n1:{road_point_type})-[r1:{road_segment}]->(n2:{road_point_type})-[r2:{road_segment}]->(n3:{road_point_type}) " \
                        "WHERE NOT (:{poi_label})-[:LOCATED_AT]->(n2) " \
                        "AND size((n2)-[:{road_segment}]-()) = 4 " \
                        "AND n1 <> n3 " \
                        "MATCH (n3)-[r3:{road_segment}]->(n2)-[r4:{road_segment}]->(n1) WITH * LIMIT 1 " \
                        "CREATE (n1)-[rr1:{road_segment} {{distance: r1.distance+r2.distance, distance_meter: r1.distance_meter+r2.distance_meter}}]->(n3) " \
                        "CREATE (n3)-[rr2:{road_segment} {{distance: r3.distance+r4.distance, distance_meter: r3.distance_meter+r4.distance_meter}}]->(n1) " \
                        "DETACH DELETE n2 " \
                        "RETURN COUNT(*)" \
                        "', {{limit:1}}) " \
                        "YIELD updates, executions " \
                        "RETURN updates" \
                        "".format(poi_label=self._poi_label, road_point_type=road_point_type, road_point=self._road_point_label, road_segment=self._road_segment_name)
                results = session.run(query)
                result = results.single()
                deleted_nodes_number += result.get("updates")
            return deleted_nodes_number

    def delete_duplicate_edges(self) -> int:
        with self._driver.session() as session:
            query = "MATCH (n1:{road_point})-[r1:{road_segment}]->(n2:{road_point})<-[r2:{road_segment}]-(n1) "\
                    "WHERE ID(r1) <> ID(r2) AND r1.distance > r2.distance "\
                    "DELETE r1" \
                    "".format(road_point=self._road_point_label, road_segment=self._road_segment_name)
            results = session.run(query)
            result = results.single()
            deleted_nodes_number = result.get("updates")
            return deleted_nodes_number


    def create_layer(self) -> None:
        with self._driver.session() as session:
            query = "CALL spatial.addPointLayerWithConfig('roadrtree','lon:lat')"
            results = session.run(query)
            result = results.single()
            print(result)

            query = "MATCH (n:RoadPoint) WITH n WITH COLLECT(n) AS m CALL spatial.addNodes('roadrtree', m) YIELD count RETURN count"
            results = session.run(query)
            result = results.single()
            print(result)

class Transformation:
    def __init__(self, config: Configuration) -> None:
        self.config = config
        if len(sys.argv) == 1 or sys.argv[1] == 'help':
            self.help()
        elif sys.argv[1] == 'info':
            self.info()
        elif sys.argv[1] == 'transform':
            self.transform()

    def help(self):
        print("This is a tool to transform a Neo4j database from the imported structure to the platooning structure.")

    def info(self):
        database = Database(self.config)
        importer_road_point_number = database.get_importer_road_point_number()
        road_point_number = database.get_road_point_number()
        print(" Road points:", importer_road_point_number + road_point_number)
        importer_road_segment_number = database.get_importer_road_segment_number()
        road_segment_number = database.get_road_segment_number()
        print(" Road segments:", importer_road_segment_number + road_segment_number)
        print("  motorways:", database.get_road_segment_number_for_type("motorway"))
        print("  motorway_links:", database.get_road_segment_number_for_type("motorway_link"))
        print("  trunks:", database.get_road_segment_number_for_type("trunk"))
        print("  trunk_links:", database.get_road_segment_number_for_type("trunk_link"))
        print("  primary:", database.get_road_segment_number_for_type("primary"))
        print("  primary_link:", database.get_road_segment_number_for_type("primary_link"))
        print(" -------------------------")
        print(" Labels transformed:", database.is_label_transformed())
        print(" Weakly connected:", database.is_weakly_connected())
        print(" Fully directed:", database.is_directed_graph())
        print(" Strongly connected:", database.is_strongly_connected())
        print(" Layers:", [layer[0] for layer in database.get_spatial_layers()])

    def transform(self):
        database = Database(self.config)
        # check if labels are transformed
        if database.is_label_transformed():
            print("+ Labels are already transformed.")
        else:
            print("- Transform labels")
            transformed_road_points, transformed_road_segments = database.transform_labels()
            print(" Transformed road points:", transformed_road_points)
            print(" Transformed road segments:", transformed_road_segments)
        # delete weakly unconnected graph components
        unconnected_components_number, unconnected_nodes_number = database.get_weakly_unconnected_components_number()
        if unconnected_components_number > 0:
            print("- Delete weakly unconnected components.")
            database.delete_weakly_unconnected_components()
            print(" Deleted components:", unconnected_components_number)
            print(" Deleted nodes:", unconnected_nodes_number)
        else:
            print("+ Graph is already weakly connected.")
        # check if graph is directed
        if database.is_directed_graph():
            print("+ Graph is already directed.")
        else:
            print("- Transform undirected edges to directed edges.")
            inserted_edes = database.insert_reverse_edges()
            print(" New edges:", inserted_edes)
        # delete strongly unconnected graph components
        unconnected_components_number, unconnected_nodes_number = database.get_strongly_unconnected_components_number()
        if unconnected_components_number > 0:
            print("- Delete strongly unconnected components.")
            database.delete_strongly_unconnected_components()
            print(" Deleted components:", unconnected_components_number)
            print(" Deleted nodes:", unconnected_nodes_number)
        else:
            print("+ Graph is already strongly connected.")
        # insert pois
        if database.exist_pois():
            print("+ Points of interest already exist.")
        else:
            print("- Import points of interest.")
            pois = PointsOfInterest.read_from_csv("poi_us.csv")
            poi_list = pois.get_poi_list()
            inserted_pois_number = database.insert_pois(poi_list)
            print(" Imported points of interest:", inserted_pois_number)
        deleted = 1
        while deleted > 0:
            deleted = 0
            # delete nodes with degree one
            print("- Delete nodes with degree one.")
            deleted_nodes_number = database.delete_road_points_with_degree_one()
            deleted += deleted_nodes_number
            print(" Deleted nodes:", deleted_nodes_number)
            # delete nodes with degree two
            print("- Delete nodes with degree two.")
            deleted_nodes_number = database.delete_road_points_with_degree_two()
            deleted += deleted_nodes_number
            print(" Deleted nodes:", deleted_nodes_number)
            # delete nodes with degree four
            print("- Delete nodes with degree four.")
            deleted_nodes_number = database.delete_road_points_with_degree_four()
            deleted += deleted_nodes_number
            print(" Deleted nodes:", deleted_nodes_number)
            print("- Delete duplicate edges.")
            deleted_edges_number = database.delete_duplicate_edges()
            deleted += deleted_edges_number
            print(" Deleted edges:", deleted_edges_number)


config = Configuration()
transformation = Transformation(config)
