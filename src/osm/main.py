import configparser
import os.path
import sys
from neo4j.v1 import GraphDatabase, Session
from typing import List, Tuple, Dict
import csv
import time
import pandas as pd
import datetime

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


class Database:
    def __init__(self, config: Configuration) -> None:
        self._driver = GraphDatabase.driver("bolt://" + config.get('host') + ":" + config.get('bolt_port'), auth=(config.get('user'), config.get('password')), max_connection_lifetime=7200)
        self._importer_road_point_label = config.get_importer('road_point_label')
        self._importer_road_segment_name = config.get_importer('road_segment_name')
        self._road_point_label = config.get('road_point_label')
        self._road_segment_name = config.get('road_segment_name')
        self._poi_label = config.get('poi_label')
        self._poi_mapping_radius_km = config.get('poi_mapping_radius_km')

    def get_number_of_nodes(self) -> int:
        query = "MATCH (n:RoadPoint) RETURN count(n) AS number_of_nodes"
        with self._driver.session() as session:
            results = session.run(query)
            result = results.single()
            return result.get("number_of_nodes")

    def get_number_of_edges(self) -> int:
        query = "MATCH ()-[r:ROAD_SEGMENT]->() RETURN count(r) AS number_of_edges"
        with self._driver.session() as session:
            results = session.run(query)
            result = results.single()
            return result.get("number_of_edges")

    def random_shortest_paths(self, number_of_paths) -> List:
        generated_ids = []

        with self._driver.session() as session:
            query = "MATCH (n:RoadPoint) WITH n WITH COUNT(n) AS road_number UNWIND range(1, " + str(number_of_paths) + ") AS i " \
                    "WITH toInteger(floor(rand()*(road_number-0.000001))) AS rnd_1, " \
                    "toInteger(floor(rand()*(road_number-1.000001))) AS rnd_2, road_number RETURN rnd_1, rnd_2"

            results = session.run(query)
            for result in results:
                rnd_1 = result.get("rnd_1")
                rnd_2 = result.get("rnd_2")
                generated_ids.append((rnd_1, rnd_2))

        return generated_ids

    def calculate_path(self, rnd_1, rnd_2) -> Dict:
        with self._driver.session() as session:
            query = "MATCH (n1:RoadPoint) WITH n1 WITH n1 SKIP " + str(rnd_1) + " LIMIT 1 " \
                    "MATCH (n2:RoadPoint) WHERE ID(n2) <> ID(n1) WITH n1, n2 SKIP " + str(rnd_2) + " LIMIT 1 " \
                    "CALL apoc.algo.aStar(n1, n2, 'ROAD_SEGMENT>', 'distance_meter', 'lat', 'lon') YIELD path, weight " \
                    "RETURN n1, n2, size(relationships(path)) AS number_of_edges, weight"

            path_info = {}
            results = session.run(query)

            for result in results:
                node_1 = result.get("n1")
                node_2 = result.get("n2")

                number_of_edges = result.get("number_of_edges")
                distance_meter = result.get("weight")

                path_info["number_of_edges"] = number_of_edges
                path_info["distance_meter"] = distance_meter
                path_info["osm_id_i"] = node_1['osm_id']
                path_info["osm_id_ii"] = node_2['osm_id']

            return path_info


class Transformation:
    def __init__(self, config: Configuration) -> None:
        self.config = config
        if len(sys.argv) == 1 or sys.argv[1] == 'help':
            self.help()
        elif sys.argv[1] == 'astar':
            self.astar()
        elif sys.argv[1] == 'spatial':
            self.astar()

    def help(self):
        print("Run experiments with: python3 main.py experiment")

    def astar(self):
        """

        """
        database = Database(self.config)

        """ Read Parameter """
        name_appendix = ""
        if len(sys.argv) > 2:
            number_of_paths = sys.argv[2]
            if len(sys.argv) > 3:
                name_appendix = sys.argv[3] + "_"
        else:
            number_of_paths = 100

        generated_ids = database.random_shortest_paths(number_of_paths)

        sum_times = 0
        df = pd.DataFrame(columns=['number_of_nodes', 'number_of_edges', 'time', "number_of_path_edges", 'distance_m', 'start_id', 'end_id', 'datetime'])

        number_of_nodes = database.get_number_of_nodes()
        number_of_edges = database.get_number_of_edges()

        i = 0
        for g in generated_ids:
            start_time = time.time()
            path_info = database.calculate_path(g[0], g[1])
            path_time = time.time() - start_time
            sum_times += path_time

            now = datetime.datetime.now()
            now = now.strftime("%Y-%m-%d %H:%M:%S")

            if path_info:  # Dict not empty
                df = df.append({'number_of_nodes': number_of_nodes, 'number_of_edges': number_of_edges,
                                'time': path_time, 'number_of_path_edges': path_info['number_of_edges'],
                                'distance_m': path_info['distance_meter'],
                                'start_id': path_info['osm_id_i'], 'end_id': path_info['osm_id_ii'],
                                'datetime': now}, ignore_index=True)
                i += 1
                print(i, path_time, path_info)

        results = df.agg({'time': ["median", "mean", "std", "sum"]})

        file_name = name_appendix + "nodes_" + str(number_of_nodes) + "_" + \
                    str(datetime.datetime.now().strftime("%Y-%m-%d__%H-%M-%S"))
        df.to_csv("results/" + file_name + ".csv", index=False)

        print(df)
        print(file_name)
        print(results)

    def spatial(self):
        print("spatial")

config = Configuration()
transformation = Transformation(config)
