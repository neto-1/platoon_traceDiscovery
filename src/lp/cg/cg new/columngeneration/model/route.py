from typing import Tuple, List


class Route(object):

    def __init__(self, route_id: int, distance: List[float], edges_path: List[Tuple[int, int]], edge_id: List[int]):
        self._route_id = route_id  # the id of the path
        self._distance = distance  # a list of distances
        self._edges_path = edges_path  # a list of tuple representing the edges
        self._edge_id = edge_id  # a list of edge-IDs

    # get the ID of the route
    def get_route_id(self) -> int:
        return self._route_id

    # get the list of distances
    def get_distance(self) -> List[float]:
        return self._distance

    # get the list of IDs of the edges in the path
    def get_edge_ids(self) -> List[int]:
        return self._edge_id

    # get the list of the edges displayed as two nodes
    def get_edges(self) -> List[Tuple[int, int]]:
        return self._edges_path
