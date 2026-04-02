from typing import Dict, Tuple

from util.cmd import CMD
from util.databasecontainer import DatabaseContainer
from util.datautil import DataUtil


class Database:
    shortest_paths = {}

    def __init__(self):
        raise NotImplementedError("static")

    @staticmethod
    def get_vehicle_locations_distance(vehicle_id: int):
        with DatabaseContainer.driver.session() as session:
            query = "MATCH (start:" + CMD.road_label + ")<-[:" + CMD.vehicle_start_rel + "]-(vehicle:" + CMD.vehicle_label + ")-[:" + CMD.vehicle_end_rel + "]->(end:" + CMD.road_label + ") " \
                                                                                                                                                                                          "WHERE id(vehicle) = " + str(
                vehicle_id) + "  RETURN [start.lon, start.lat] as start, [end.lon, end.lat] as end, vehicle.shortest_path_distance AS distance"
            results = session.run(query)
            result = results.single()

            start = result.get("start")
            end = result.get("end")

            distance = result.get("distance")

            return start, end, distance

    @staticmethod
    def get_vehicle_shortest_path(vehicle_id: int) -> Tuple[float, Dict]:
        if vehicle_id not in Database.shortest_paths:
            with DatabaseContainer.driver.session() as session:
                query = "MATCH (end:" + CMD.road_label + ")<-[r2:" + CMD.vehicle_end_rel + "]-(v:" + CMD.vehicle_label + ")-[r1:" + CMD.vehicle_start_rel + "]->(start:" + CMD.road_label + ") " \
                                                                                                                                                                                            "WHERE id(v)=" + str(
                    vehicle_id) + " with start, end " \
                                  "CALL apoc.algo.aStar(start, end, '" + CMD.road_rel + ">', 'distance_meter','lat','lon')  YIELD weight, path RETURN weight, path"
                results = session.run(query)
                result = results.single()

                weight = result.get("weight")
                path = result.get("path")

                Database.shortest_paths[vehicle_id] = DataUtil.create_path_from_path_result(weight, path)

        return Database.shortest_paths[vehicle_id]

    @staticmethod
    def clean_cached_shortest_paths():
        Database.shortest_paths.clear()
