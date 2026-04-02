from columngeneration.model.route import Route
from typing import List


class Vehicle(object):
    def __init__(self, db, vehicle_id: int, start: int, end: int):
        self._vehicle_id = vehicle_id
        self._path = []
        self._db = db
        self._start = start
        self._end = end
        self._polygon = []

    # get the starting node
    def get_start(self) -> int:
        return self._start

    # get the ending node
    def get_end(self) -> int:
        return self._end

    # add a path to the list of paths
    def add_path(self, path: Route) -> None:
        self._path.append(path)

    # store the (unique) polygon as a list of points
    def store_polygon(self, polygon: List[float]) -> None:
        self._polygon.append(polygon)

    # get the list of paths
    def get_paths(self, number: int) -> Route:
        return self._path[number-1]

    # get a list of all paths
    def get_all_paths(self) -> List[Route]:
        return self._path

    # get the polygon as a list of points
    def get_polygon(self) -> List[float]:
        return self._polygon[0]

    # get the id of the vehicle
    def get_id(self) -> int:
        return self._vehicle_id

    # delete ALL paths
    def delete_paths(self) -> None:
        del self._path[:]

    def add_relevant_paths_pl(self):
        if self.get_id() == 0:
            self.add_path(Route(7, [33.7, 30, 30, 30, 30, 30, 33.7], [(10, 21), (21, 31), (31, 41), (41, 51), (51, 61), (61, 71), (71, 80)], [260, 18, 26, 34, 42, 50, 262]))

        #if self.get_id() == 18:
        #    self.add_path(Route(8, [33.7, 30, 30, 30, 30, 30, 33.7], [(12, 21), (21, 31), (31, 41), (41, 51), (51, 61), (61, 71), (71, 82)], [261, 18, 26, 34, 42, 50, 263]))
